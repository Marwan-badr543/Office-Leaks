import React, { useState, useEffect, useMemo, useRef, useCallback } from "react";
import { 
  MapPin, 
  Clock, 
  Search, 
  ChevronLeft, 
  Lock, 
  MessageSquare, 
  ShieldCheck,
  Building,
  AtSign,
  Heart,
  Settings,
  Edit3,
  Camera,
  KeyRound,
  LogOut,
  AlertTriangle,
  Info,
  X,
  Trash2
} from "lucide-react";
import type { User, Post } from "../types";
import { usersApi } from "../api/usersApi";
import { useDebounce } from "../hooks/useDebounce";
import { useScrollMemory } from "../hooks/useScrollMemory";
import { ConfirmActionModal } from "./ConfirmActionModal";
import { PostCard } from "./PostCard";
import { postsApi } from "../api/postsApi";

interface PeersViewProps {
  currentUser?: User;
  mode?: "directory" | "profile";
  onOpenAuthModal?: () => void;
  onCompanyClick?: (companyId: string) => void;
}

export const PeersView: React.FC<PeersViewProps> = ({ 
  currentUser, 
  mode = "directory",
  onOpenAuthModal,
  onCompanyClick
}) => {
  const [userList, setUserList] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const debouncedSearchTerm = useDebounce(searchTerm, 250);
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"posts" | "reviews">("posts");
  const [isMobileProfileView, setIsMobileProfileView] = useState(false);
  const [userPosts, setUserPosts] = useState<Post[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [loadingPosts, setLoadingPosts] = useState(false);

  // Settings & Edit UI States
  const [showSettingsDropdown, setShowSettingsDropdown] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editSuccessMessage, setEditSuccessMessage] = useState("");
  const [editErrorMessage, setEditErrorMessage] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);

  // Edit Form Fields
  const [editFirstName, setEditFirstName] = useState("");
  const [editLastName, setEditLastName] = useState("");
  const [editAge, setEditAge] = useState<number>(25);
  const [editGender, setEditGender] = useState<"MALE" | "FEMALE">("MALE");
  const [editCountry, setEditCountry] = useState("");
  const [editCompany, setEditCompany] = useState("");
  const [editBio, setEditBio] = useState("");

  // Change Password Form Fields
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [changingPassword, setChangingPassword] = useState(false);

  // Profile Image Upload State
  const [uploadingImage, setUploadingImage] = useState(false);

  // AbortControllers and fetch tracker refs to prevent duplicate/concurrent requests
  const directoryAbortControllerRef = useRef<AbortController | null>(null);
  const postsAbortControllerRef = useRef<AbortController | null>(null);
  const isFetchingUsersRef = useRef<boolean>(false);
  const lastLoadedUserIdRef = useRef<string | null>(null);

  useScrollMemory("peers");

  // Shallow URL syncing for selected user profile
  useEffect(() => {
    if (mode !== "profile" && selectedUserId) {
      const url = new URL(window.location.href);
      url.searchParams.set("user", selectedUserId);
      window.history.replaceState({}, "", url.toString());
    }
  }, [selectedUserId, mode]);

  // Load user directory from API
  useEffect(() => {
    if (mode === "profile") {
      setLoadingUsers(false);
      return;
    }

    // Deduplication check
    if (isFetchingUsersRef.current) return;
    isFetchingUsersRef.current = true;

    // Abort active directory fetch
    if (directoryAbortControllerRef.current) {
      directoryAbortControllerRef.current.abort();
    }
    const controller = new AbortController();
    directoryAbortControllerRef.current = controller;

    setLoadingUsers(true);

    usersApi
      .getUsers({ page: 1, pageSize: 50 })
      .then((res) => {
        if (controller.signal.aborted) return;
        const users = res.users || [];
        setUserList(users);

        const urlParams = new URLSearchParams(window.location.search);
        const urlUserId = urlParams.get("user");

        if (urlUserId && users.some((u) => u.id === urlUserId)) {
          setSelectedUserId(urlUserId);
          setIsMobileProfileView(true);
        } else if (users.length > 0) {
          setSelectedUserId(users[0].id);
        } else if (currentUser) {
          setSelectedUserId(currentUser.id);
        }
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        console.error("Failed to fetch users from backend:", err);
      })
      .finally(() => {
        isFetchingUsersRef.current = false;
        setLoadingUsers(false);
      });

    return () => {
      controller.abort();
      isFetchingUsersRef.current = false;
    };
  }, [currentUser, mode]);

  // Selected user object
  const selectedUser = useMemo(() => {
    if (mode === "profile") {
      return currentUser || {
        id: "1",
        name: "User #1",
        username: "user_1",
        avatar: "",
        title: "Corporate Professional",
        location: "Riyadh, KSA",
        country: "Saudi Arabia",
        gender: "MALE" as const,
        age: 25,
        bio: "",
        companyName: ""
      };
    }
    return userList.find((u) => u.id === selectedUserId) || currentUser || {
      id: "1",
      name: "User #1",
      username: "user_1",
      avatar: "",
      title: "Corporate Professional",
      location: "Riyadh, KSA",
      country: "Saudi Arabia",
      gender: "MALE" as const,
      age: 25,
      bio: "",
      companyName: ""
    };
  }, [userList, selectedUserId, currentUser, mode]);

  // Initialize edit fields when edit modal opens
  useEffect(() => {
    if (showEditModal && currentUser) {
      setEditFirstName(currentUser.firstName || "");
      setEditLastName(currentUser.lastName || "");
      setEditAge(currentUser.age || 25);
      setEditGender(currentUser.gender || "MALE");
      setEditCountry(currentUser.country || "");
      setEditCompany(currentUser.companyName || "");
      setEditBio(currentUser.bio || "");
      setEditErrorMessage("");
      setEditSuccessMessage("");
    }
  }, [showEditModal, currentUser]);

  // Load user specific posts from API
  useEffect(() => {
    if (!selectedUser.id) {
      setUserPosts([]);
      return;
    }

    if (lastLoadedUserIdRef.current === selectedUser.id) {
      return;
    }
    lastLoadedUserIdRef.current = selectedUser.id;

    // Abort active posts fetch
    if (postsAbortControllerRef.current) {
      postsAbortControllerRef.current.abort();
    }
    const controller = new AbortController();
    postsAbortControllerRef.current = controller;

    setLoadingPosts(true);

    usersApi
      .getUserPosts(selectedUser.id)
      .then((postsFetched) => {
        if (controller.signal.aborted) return;
        setUserPosts(postsFetched || []);
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        console.error("Failed to fetch user posts:", err);
        setUserPosts([]);
        lastLoadedUserIdRef.current = null;
      })
      .finally(() => {
        setLoadingPosts(false);
      });

    return () => {
      controller.abort();
      lastLoadedUserIdRef.current = null;
    };
  }, [selectedUser.id]);

  // Filtered users directory list with debounced search
  const filteredUsers = useMemo(() => {
    return userList.filter((u) => {
      const matchName = u.name.toLowerCase().includes(debouncedSearchTerm.toLowerCase());
      const matchTitle = u.title.toLowerCase().includes(debouncedSearchTerm.toLowerCase());
      const matchComp = u.companyName?.toLowerCase().includes(debouncedSearchTerm.toLowerCase());
      return matchName || matchTitle || matchComp;
    });
  }, [userList, debouncedSearchTerm]);

  const handleSelectUser = (id: string) => {
    setSelectedUserId(id);
    setIsMobileProfileView(true);
  };

  const handleLikePost = useCallback(
    (postId: string) => {
      if (!currentUser) {
        if (onOpenAuthModal) onOpenAuthModal();
        return;
      }

      let wasLikedPreviously = false;

      setUserPosts((prev) =>
        prev.map((post) => {
          if (post.id === postId) {
            wasLikedPreviously = !!post.hasLiked;
            const isLiking = !post.hasLiked;
            return {
              ...post,
              hasLiked: isLiking,
              likesCount: Math.max(0, post.likesCount + (isLiking ? 1 : -1)),
            };
          }
          return post;
        })
      );

      const userId = Number(currentUser.id) || 1;
      const apiCall = wasLikedPreviously
        ? postsApi.unlikePost(postId, userId)
        : postsApi.likePost(postId, userId);

      apiCall.catch((err) => {
        console.error("Optimistic Like mutation failed, rolling back:", err);
        setUserPosts((prev) =>
          prev.map((post) => {
            if (post.id === postId) {
              return {
                ...post,
                hasLiked: wasLikedPreviously,
                likesCount: Math.max(0, post.likesCount + (wasLikedPreviously ? 1 : -1)),
              };
            }
            return post;
          })
        );
      });
    },
    [currentUser, onOpenAuthModal]
  );

  const handleSavePost = useCallback(
    (postId: string) => {
      setUserPosts((prev) =>
        prev.map((post) => {
          if (post.id === postId) {
            return { ...post, hasSaved: !post.hasSaved };
          }
          return post;
        })
      );
    },
    []
  );

  // Sign out implementation
  const handleSignOut = () => {
    localStorage.removeItem("office_leaks_user");
    localStorage.removeItem("office_leaks_token");
    localStorage.removeItem("office_leaks_refresh_token");
    localStorage.removeItem("office_leaks_active_tab");
    
    // Clear URL parameters
    const url = new URL(window.location.href);
    url.searchParams.delete("tab");
    url.searchParams.delete("user");
    window.history.replaceState({}, "", url.toString());

    window.location.reload();
  };

  // Delete account implementation
  const handleDeleteAccount = async () => {
    try {
      await usersApi.deleteAccount();
      // Clear localStorage and redirect just like Sign Out
      localStorage.removeItem("office_leaks_user");
      localStorage.removeItem("office_leaks_token");
      localStorage.removeItem("office_leaks_refresh_token");
      localStorage.removeItem("office_leaks_active_tab");
      
      const url = new URL(window.location.href);
      url.searchParams.delete("tab");
      url.searchParams.delete("user");
      window.history.replaceState({}, "", url.toString());

      window.location.reload();
    } catch (err) {
      console.error("Failed to delete account:", err);
      alert("Failed to delete account. Please try again later.");
    }
  };

  // Update profile handler
  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setEditErrorMessage("");
    setEditSuccessMessage("");
    
    if (!editFirstName.trim() || !editLastName.trim()) {
      setEditErrorMessage("First name and Last name are required.");
      return;
    }

    setSavingProfile(true);
    try {
      const updated = await usersApi.updateUser({
        first_name: editFirstName.trim(),
        last_name: editLastName.trim(),
        age: editAge,
        gender: editGender,
        country: editCountry.trim(),
        current_company: editCompany.trim(),
        about: editBio.trim()
      });

      // Update state in memory & localStorage
      localStorage.setItem("office_leaks_user", JSON.stringify(updated));
      setEditSuccessMessage("Profile updated successfully!");
      
      // Delay modal close to let the user see success message
      setTimeout(() => {
        setShowEditModal(false);
        window.location.reload(); // Reload to refresh profile data across all instances
      }, 1000);
    } catch (err) {
      console.error("Failed to update profile:", err);
      setEditErrorMessage("Error updating profile. Please try again.");
    } finally {
      setSavingProfile(false);
    }
  };

  // Change password handler
  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError("");
    setPasswordMessage("");

    if (!oldPassword || !newPassword || !confirmPassword) {
      setPasswordError("All fields are required.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match.");
      return;
    }

    if (newPassword.length < 6) {
      setPasswordError("New password must be at least 6 characters.");
      return;
    }

    setChangingPassword(true);
    try {
      await usersApi.changePassword({
        old_password: oldPassword,
        new_password: newPassword
      });
      setPasswordMessage("Password changed successfully!");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => {
        setShowChangePassword(false);
        setShowEditModal(false);
        setPasswordMessage("");
      }, 1500);
    } catch (err: any) {
      console.error("Failed to change password:", err);
      const detail = err.response?.data?.detail || "Current password is incorrect.";
      setPasswordError(detail);
    } finally {
      setChangingPassword(false);
    }
  };

  // Image Upload handler
  const handleImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Basic size validation (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert("Image is too large. Max size is 5MB.");
      return;
    }

    setUploadingImage(true);
    try {
      const { image_url } = await usersApi.uploadProfileImage(file);
      
      // If upload succeeds, update the active user's details
      if (currentUser) {
        const updatedUser = { ...currentUser, avatar: image_url };
        localStorage.setItem("office_leaks_user", JSON.stringify(updatedUser));
        window.location.reload(); // Reload to refresh headers/sidebar & profile
      }
    } catch (err) {
      console.error("Image upload failed:", err);
      alert("Image upload failed. Please try again.");
    } finally {
      setUploadingImage(false);
    }
  };

  const isSelf = currentUser && selectedUser.id === currentUser.id;

  return (
    <div className="flex flex-col md:flex-row gap-5 h-[calc(100vh-140px)] md:h-[calc(100vh-100px)] overflow-hidden">
      {/* LEFT COLUMN: Peer Directory List */}
      {mode !== "profile" && (
        <div 
          className={`w-full md:w-5/12 lg:w-4/12 flex flex-col bg-white border border-slate-100 rounded-2xl overflow-hidden shadow-sm ${
            isMobileProfileView ? "hidden md:flex" : "flex"
          }`}
        >
          <div className="p-4 border-b border-slate-100 space-y-3">
            <h2 className="text-sm font-bold text-slate-800 font-heading">
              Peer Network
            </h2>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search peers by name or title..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9] focus:border-[#0EA5E9]"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {loadingUsers ? (
              <p className="text-xs text-slate-400 italic text-center py-8">
                Loading users from database...
              </p>
            ) : (
              filteredUsers.map((user) => {
                const isSelected = user.id === selectedUserId;
                const isUserSelf = currentUser && user.id === currentUser.id;
                return (
                  <div
                    key={user.id}
                    onClick={() => handleSelectUser(user.id)}
                    className={`p-3 rounded-xl border cursor-pointer transition-all duration-200 flex items-center justify-between ${
                      isSelected
                        ? "bg-[#0EA5E9]/5 border-[#0EA5E9] shadow-sm"
                        : "bg-white border-slate-100 hover:border-slate-200"
                    }`}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <img
                        src={user.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.id}`}
                        alt={user.name}
                        className="w-10 h-10 rounded-full border border-slate-100 object-cover flex-shrink-0 bg-slate-50"
                      />
                      <div className="min-w-0">
                        <h3 className="font-bold text-slate-800 text-xs font-heading truncate flex items-center gap-1.5">
                          {user.name}
                          {isUserSelf && (
                            <span className="text-[8px] bg-slate-100 text-slate-500 font-extrabold px-1 rounded">
                              YOU
                            </span>
                          )}
                        </h3>
                        <p className="text-[10px] text-slate-400 mt-0.5 truncate leading-tight">
                          {user.title} {user.companyName && `@ ${user.companyName}`}
                        </p>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSelectUser(user.id);
                      }}
                      className={`text-[9px] font-bold px-2 py-1.5 rounded-lg border transition-all cursor-pointer ${
                        isSelected 
                          ? "bg-[#0EA5E9] border-[#0EA5E9] text-white" 
                          : "bg-slate-50 border-slate-200 text-slate-650 hover:bg-slate-100"
                      }`}
                    >
                      View Profile
                    </button>
                  </div>
                );
              })
            )}

            {!loadingUsers && filteredUsers.length === 0 && (
              <p className="text-xs text-slate-400 italic text-center py-8">
                No peers found.
              </p>
            )}
          </div>
        </div>
      )}

      {/* RIGHT COLUMN: Profile Detail View */}
      <div 
        className={`flex-1 flex flex-col bg-white border border-slate-100 rounded-2xl overflow-y-auto shadow-sm relative ${
          mode === "profile"
            ? "flex"
            : (!isMobileProfileView ? "hidden md:flex" : "flex")
        }`}
      >
        {/* Profile Header Banner */}
        <div className="relative h-24 lg:h-28 bg-[#0F172A] flex-shrink-0">
          {mode !== "profile" && (
            <button
              onClick={() => setIsMobileProfileView(false)}
              className="md:hidden absolute top-4 left-4 bg-white/90 text-slate-800 p-2 rounded-xl backdrop-blur-sm shadow-md cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
          )}
          
          <div className="absolute top-4 right-4 flex items-center gap-1.5 text-slate-450 bg-slate-900/60 px-2 py-1 rounded-lg backdrop-blur-sm border border-slate-800">
            <Clock className="w-3.5 h-3.5" />
            <span className="text-[10px] font-medium font-body text-slate-200">
              {selectedUser.timezone || "GMT+3"}
            </span>
          </div>
        </div>

        {/* Profile Info Details */}
        <div className="px-6 pb-4 relative border-b border-slate-100 flex-shrink-0">
          {/* Avatar Picture with custom upload button for own profile */}
          <div className="absolute -top-10 left-6 group">
            <div className="relative w-16 h-16 rounded-2xl border-4 border-white shadow-md overflow-hidden bg-white">
              <img
                src={selectedUser.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${selectedUser.id}`}
                alt={selectedUser.name}
                className="w-full h-full object-cover"
              />
              {isSelf && (
                <label className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer text-[8px] font-bold">
                  <Camera className="w-4 h-4 mb-0.5" />
                  {uploadingImage ? "Uploading..." : "Change"}
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="hidden"
                    disabled={uploadingImage}
                  />
                </label>
              )}
            </div>
          </div>

          <div className="pt-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <h1 className="text-base lg:text-lg font-extrabold font-heading text-slate-800 flex items-center gap-1.5 leading-none">
                {selectedUser.name}
                <ShieldCheck className="w-4 h-4 text-[#0EA5E9]" />
              </h1>
              <div className="flex items-center gap-2 text-xs text-slate-400 mt-2 font-medium">
                <span className="flex items-center gap-0.5">
                  <AtSign className="w-3 h-3" />
                  {selectedUser.username}
                </span>
                <span>•</span>
                <span className="flex items-center gap-0.5">
                  <Building className="w-3 h-3" />
                  {selectedUser.title} {selectedUser.companyName && `at ${selectedUser.companyName}`}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-400 mt-1.5 font-medium">
                <span className="flex items-center gap-1 bg-slate-50 border border-slate-100 rounded-md px-1.5 py-0.5">
                  <MapPin className="w-3 h-3" /> {selectedUser.location}
                </span>
                {selectedUser.age !== undefined && (
                  <span className="bg-slate-50 border border-slate-100 rounded-md px-1.5 py-0.5">
                    Age: {selectedUser.age}
                  </span>
                )}
                {selectedUser.gender && (
                  <span className="bg-slate-50 border border-slate-100 rounded-md px-1.5 py-0.5 capitalize">
                    Gender: {selectedUser.gender.toLowerCase()}
                  </span>
                )}
              </div>
            </div>

            {/* Profile Action Buttons & Settings Dropdown (Self Only) */}
            {isSelf && (
              <div className="flex items-center gap-2 relative">
                <button
                  onClick={() => setShowEditModal(true)}
                  className="flex items-center gap-1 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 font-bold px-3 py-1.5 rounded-xl text-xs transition-colors cursor-pointer"
                >
                  <Edit3 className="w-3.5 h-3.5" />
                  Edit Profile
                </button>
                <div className="relative">
                  <button
                    onClick={() => setShowSettingsDropdown(!showSettingsDropdown)}
                    className="p-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 rounded-xl transition-colors cursor-pointer"
                    title="Account Settings"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                  {showSettingsDropdown && (
                    <div className="absolute right-0 mt-2 w-44 bg-white border border-slate-100 rounded-xl shadow-xl z-20 py-1 text-xs">
                      <button
                        onClick={() => {
                          setShowSettingsDropdown(false);
                          setShowLogoutConfirm(true);
                        }}
                        className="w-full flex items-center gap-2 px-3 py-2 text-slate-700 hover:bg-slate-50 text-left cursor-pointer"
                      >
                        <LogOut className="w-3.5 h-3.5 text-slate-400" />
                        Log Out
                      </button>
                      <button
                        onClick={() => {
                          setShowSettingsDropdown(false);
                          setShowDeleteConfirm(true);
                        }}
                        className="w-full flex items-center gap-2 px-3 py-2 text-[#EF4444] hover:bg-red-50 text-left font-semibold cursor-pointer border-t border-slate-50"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        Delete Account
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {selectedUser.bio && (
            <div className="mt-4">
              <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1 font-heading">
                About Me
              </h4>
              <p className="text-xs text-slate-600 leading-relaxed font-body">
                {selectedUser.bio}
              </p>
            </div>
          )}
        </div>

        {/* Profile Tabs */}
        <div className="flex-shrink-0 border-b border-slate-100 flex px-6">
          <button
            onClick={() => setActiveTab("posts")}
            className={`py-3 px-4 font-heading text-xs font-bold border-b-2 transition-all relative cursor-pointer ${
              activeTab === "posts"
                ? "border-[#0EA5E9] text-[#0EA5E9]"
                : "border-transparent text-slate-400 hover:text-slate-700"
            }`}
          >
            Public Posts ({userPosts.length})
          </button>
          <button
            onClick={() => setActiveTab("reviews")}
            className={`py-3 px-4 font-heading text-xs font-bold border-b-2 transition-all relative cursor-pointer ${
              activeTab === "reviews"
                ? "border-[#0EA5E9] text-[#0EA5E9]"
                : "border-transparent text-slate-400 hover:text-slate-700"
            }`}
          >
            Public Reviews
          </button>
        </div>

        {/* Tab Contents */}
        <div className="p-5 bg-slate-50/50">
          {activeTab === "posts" ? (
            <div className="space-y-4">
              {loadingPosts ? (
                <p className="text-xs text-slate-400 italic text-center py-10 bg-white border border-slate-100 rounded-2xl">
                  Loading posts...
                </p>
              ) : (
                userPosts.map((post) => (
                  <PostCard
                    key={post.id}
                    post={post}
                    currentUser={currentUser}
                    onOpenAuthModal={onOpenAuthModal}
                    onLike={handleLikePost}
                    onSave={handleSavePost}
                    onNavigateToUser={(userId) => setSelectedUserId(userId)}
                    onCompanyClick={onCompanyClick}
                  />
                ))
              )}

              {!loadingPosts && userPosts.length === 0 && (
                <p className="text-xs text-slate-400 italic text-center py-10 bg-white border border-slate-100 rounded-2xl">
                  This user has not posted any public updates yet.
                </p>
              )}
            </div>
          ) : (
            <div className="bg-white border border-slate-100 rounded-2xl p-6 text-center space-y-4 shadow-sm max-w-md mx-auto mt-4">
              <div className="w-12 h-12 bg-slate-900 text-white rounded-full flex items-center justify-center mx-auto shadow-sm">
                <Lock className="w-5 h-5 text-[#0EA5E9]" />
              </div>
              <div>
                <h3 className="font-extrabold text-slate-800 text-sm font-heading">
                  Reviews Cryptographically Hashed
                </h3>
                <p className="text-xs text-slate-500 mt-2 leading-relaxed font-body">
                  To ensure complete protection for whistleblowers, all company reviews and ratings are cryptographically dissociated from employee user profiles. 
                </p>
                <div className="bg-slate-50 rounded-xl p-3 text-[10px] text-slate-400 border border-slate-100 text-left mt-4 font-body leading-normal">
                  🔐 <strong>Security Protocol:</strong> Reviews are indexed solely by tagged company ID. Profile links are never written to the review payload, preventing correlation attacks.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* EDIT PROFILE MODAL */}
      {showEditModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-slate-100 rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden font-body animate-in fade-in zoom-in-95 duration-150 relative max-h-[90vh] flex flex-col">
            
            {/* Header */}
            <div className="bg-[#0F172A] p-5 text-white flex items-center justify-between border-b border-slate-800 flex-shrink-0">
              <div className="flex items-center gap-3">
                <Edit3 className="w-5 h-5 text-[#0EA5E9] stroke-[2.5]" />
                <div>
                  <h2 className="text-sm font-extrabold font-heading">Edit Profile</h2>
                  <p className="text-[10px] text-slate-300 mt-0.5">Customize your public professional identity</p>
                </div>
              </div>
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setShowChangePassword(false);
                }}
                className="text-slate-400 hover:text-white p-1 rounded-xl transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Scrollable Form Body */}
            <div className="p-6 overflow-y-auto flex-1 space-y-5 text-xs">
              
              {editErrorMessage && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-xl flex items-center gap-2">
                  <Info className="w-4 h-4 text-red-500 flex-shrink-0" />
                  <span>{editErrorMessage}</span>
                </div>
              )}

              {editSuccessMessage && (
                <div className="bg-green-50 border border-green-200 text-green-700 p-3 rounded-xl flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span>{editSuccessMessage}</span>
                </div>
              )}

              {/* Main Fields Form */}
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                
                {/* Readonly Username (Email) */}
                <div className="space-y-1 bg-slate-50 border border-slate-100 rounded-xl p-3">
                  <label className="font-bold text-slate-500 uppercase tracking-wider text-[9px]">Username (Cannot change)</label>
                  <p className="font-medium text-slate-700 text-sm font-heading select-all">@{currentUser?.username}</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="font-bold text-slate-700">First Name</label>
                    <input
                      type="text"
                      value={editFirstName}
                      onChange={(e) => setEditFirstName(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9]"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="font-bold text-slate-700">Last Name</label>
                    <input
                      type="text"
                      value={editLastName}
                      onChange={(e) => setEditLastName(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9]"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="space-y-1">
                    <label className="font-bold text-slate-700">Age</label>
                    <input
                      type="number"
                      min={18}
                      max={100}
                      value={editAge}
                      onChange={(e) => setEditAge(parseInt(e.target.value) || 25)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9]"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="font-bold text-slate-700">Country</label>
                    <input
                      type="text"
                      value={editCountry}
                      onChange={(e) => setEditCountry(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9]"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="font-bold text-slate-700">Gender</label>
                    <select
                      value={editGender}
                      onChange={(e) => setEditGender(e.target.value as "MALE" | "FEMALE")}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl px-2 py-2 text-slate-800 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9] font-heading font-bold"
                    >
                      <option value="MALE">Male</option>
                      <option value="FEMALE">Female</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="font-bold text-slate-700">Current Company</label>
                  <input
                    type="text"
                    value={editCompany}
                    onChange={(e) => setEditCompany(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9]"
                  />
                </div>

                <div className="space-y-1">
                  <label className="font-bold text-slate-700">About Me (Bio)</label>
                  <textarea
                    value={editBio}
                    onChange={(e) => setEditBio(e.target.value)}
                    rows={3}
                    maxLength={1000}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9] resize-none"
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditModal(false);
                      setShowChangePassword(false);
                    }}
                    className="flex-1 py-3 rounded-xl border border-slate-200 text-slate-500 hover:bg-slate-50 font-bold text-xs font-heading transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={savingProfile}
                    className={`flex-2 py-3 rounded-xl font-extrabold text-white text-xs font-heading shadow-md transition-all ${
                      savingProfile
                        ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                        : "bg-[#0EA5E9] hover:bg-[#0EA5E9]/90 active:scale-[0.98] cursor-pointer shadow-[#0EA5E9]/20"
                    }`}
                  >
                    {savingProfile ? "Saving..." : "Save Details"}
                  </button>
                </div>
              </form>

              {/* Collapsible Change Password Section */}
              <div className="border-t border-slate-100 pt-4">
                <button
                  onClick={() => setShowChangePassword(!showChangePassword)}
                  className="flex items-center justify-between w-full py-2 text-slate-650 hover:text-slate-800 font-bold font-heading cursor-pointer"
                >
                  <span className="flex items-center gap-1.5">
                    <KeyRound className="w-4 h-4 text-slate-400" />
                    Security & Password Change
                  </span>
                  <span className="text-[10px] text-slate-400 hover:underline">
                    {showChangePassword ? "Hide Options" : "Show Options"}
                  </span>
                </button>

                {showChangePassword && (
                  <form onSubmit={handleChangePassword} className="space-y-3 mt-3 p-4 bg-slate-50 border border-slate-100 rounded-xl">
                    {passwordError && <p className="text-[10px] text-[#EF4444] font-bold">{passwordError}</p>}
                    {passwordMessage && <p className="text-[10px] text-green-600 font-bold">{passwordMessage}</p>}

                    <div className="space-y-1">
                      <label className="font-bold text-slate-700">Current Password</label>
                      <input
                        type="password"
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                        className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-slate-855 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9]"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="space-y-1">
                        <label className="font-bold text-slate-700">New Password</label>
                        <input
                          type="password"
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-slate-855 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9]"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="font-bold text-slate-700">Confirm New Password</label>
                        <input
                          type="password"
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-slate-855 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9]"
                        />
                      </div>
                    </div>
                    <button
                      type="submit"
                      disabled={changingPassword}
                      className={`w-full py-2 rounded-xl font-bold text-white text-[11px] font-heading shadow-sm transition-all ${
                        changingPassword
                          ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                          : "bg-[#0F172A] hover:bg-slate-850 cursor-pointer"
                      }`}
                    >
                      {changingPassword ? "Updating..." : "Update Password"}
                    </button>
                  </form>
                )}
              </div>

            </div>
          </div>
        </div>
      )}

      {/* CONFIRMATION MODALS */}
      <ConfirmActionModal
        isOpen={showLogoutConfirm}
        onClose={() => setShowLogoutConfirm(false)}
        onConfirm={handleSignOut}
        title="Confirm Sign Out"
        message="Are you sure you want to end your secure session? You will need to sign back in to access decrypted corporate leaks."
        confirmText="Sign Out"
        icon={LogOut}
      />

      <ConfirmActionModal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDeleteAccount}
        title="Permanently Delete Account"
        message="Warning: This is destructive and irreversible. Your whistleblower credentials, custom image, and profile statistics will be deleted from the database immediately."
        confirmText="Delete Account"
        confirmBgClass="bg-[#EF4444]"
        confirmHoverClass="hover:bg-[#DC2626]"
        icon={AlertTriangle}
        iconColorClass="text-[#EF4444]"
        iconBgClass="bg-red-50 animate-pulse"
      />
    </div>
  );
};
