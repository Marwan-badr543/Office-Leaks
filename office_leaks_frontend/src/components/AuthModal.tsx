import React, { useState } from "react";
import {
  ShieldAlert, Lock, User as UserIcon, Globe, Calendar,
  Eye, EyeOff, AlertCircle, Shield, Building, FileText, ChevronRight, ChevronLeft,
} from "lucide-react";
import type { User } from "../types";
import { usersApi } from "../api/usersApi";
import { companiesApi } from "../api/companiesApi";
import maleAvatar from "../assets/male_avatar.svg";
import femaleAvatar from "../assets/female_avatar.svg";

interface AuthPageProps {
  onAuthSuccess: (user: User) => void;
  onClose?: () => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onAuthSuccess, onClose }) => {
  const [activeTab, setActiveTab] = useState<"signin" | "register">("signin");
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Registration step (multi-step form)
  const [regStep, setRegStep] = useState<1 | 2>(1);

  // Sign In
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Register Step 1
  const [regUsername, setRegUsername] = useState("");
  const [regFirstName, setRegFirstName] = useState("");
  const [regLastName, setRegLastName] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regAge, setRegAge] = useState<number>(25);
  const [regCountry, setRegCountry] = useState("Saudi Arabia");
  const [regGender, setRegGender] = useState<"MALE" | "FEMALE">("MALE");

  // Register Step 2
  const [regAbout, setRegAbout] = useState("");
  const [regCompany, setRegCompany] = useState("");
  const [emailError, setEmailError] = useState("");

  const validateEmail = (emailStr: string) => {
    if (!emailStr.trim()) {
      setEmailError("Email is required.");
      return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailStr.trim())) {
      setEmailError("Please enter a valid email address.");
      return false;
    }
    setEmailError("");
    return true;
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    if (!loginUsername.trim() || !loginPassword.trim()) {
      setErrorMessage("Please enter both username and password.");
      return;
    }

    setSubmitting(true);
    try {
      const tokens = await usersApi.login({
        username: loginUsername.trim(),
        password: loginPassword.trim(),
      });

      if (tokens.access) {
        localStorage.setItem("office_leaks_token", tokens.access);
      }

      let authenticatedUser: User;
      try {
        const base64Url = tokens.access.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
          window.atob(base64)
            .split('')
            .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
            .join('')
        );
        const payload = JSON.parse(jsonPayload);
        const userId = String(payload.user_id);
        authenticatedUser = await usersApi.getUserById(userId);
      } catch (err) {
        console.error("Failed to decode token or fetch user profile:", err);
        authenticatedUser = {
          id: "1",
          name: loginUsername.trim(),
          username: loginUsername.trim(),
          avatar: maleAvatar,
          title: "Verified Employee",
          location: "Saudi Arabia",
        };
      }

      localStorage.setItem("office_leaks_user", JSON.stringify(authenticatedUser));
      onAuthSuccess(authenticatedUser);
    } catch (err: unknown) {
      console.error("Sign in failed:", err);
      const error = err as { response?: { data?: { detail?: string; non_field_errors?: string[] } } };
      const detail = error.response?.data?.detail || error.response?.data?.non_field_errors?.[0] || "Invalid credentials. Please check your username and password.";
      setErrorMessage(typeof detail === "string" ? detail : "Sign in failed. Invalid username or password.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    if (!regUsername.trim() || !regFirstName.trim() || !regLastName.trim() || !regPassword.trim()) {
      setErrorMessage("Please fill in all required fields.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(regUsername.trim())) {
      setErrorMessage("Username must be a valid email address.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await usersApi.createUser({
        username: regUsername.trim(),
        first_name: regFirstName.trim(),
        last_name: regLastName.trim(),
        password: regPassword.trim(),
        age: regAge,
        country: regCountry,
        gender: regGender,
        about: regAbout.trim() || undefined,
        current_company: regCompany.trim() || undefined,
      });

      const fullName = `${regFirstName.trim()} ${regLastName.trim()}`;
      const newUser: User = {
        id: String(res.id || Date.now()),
        name: fullName,
        username: res.username || regUsername.trim(),
        avatar: regGender === "FEMALE" ? femaleAvatar : maleAvatar,
        title: "Corporate Member",
        location: regCountry,
        gender: regGender,
        age: regAge,
        bio: regAbout.trim() || undefined,
        companyName: regCompany.trim() || undefined,
        country: regCountry,
        firstName: regFirstName.trim(),
        lastName: regLastName.trim(),
      };

      // Auto-login after registration
      try {
        const tokens = await usersApi.login({
          username: regUsername.trim(),
          password: regPassword.trim(),
        });
        if (tokens.access) {
          localStorage.setItem("office_leaks_token", tokens.access);
          // If the user specified a company, send it to the AI creation endpoint
          if (regCompany && regCompany.trim()) {
            companiesApi.createCompanyWithAi(regCompany.trim()).catch((err) => {
              console.error("Auto-creating company on register failed:", err);
            });
          }
        }
      } catch {
        // Continue with session profile if login token call fails
      }

      localStorage.setItem("office_leaks_user", JSON.stringify(newUser));
      onAuthSuccess(newUser);
    } catch (err: unknown) {
      console.error("Registration failed:", err);
      const error = err as { response?: { data?: Record<string, unknown> } };
      const data = error.response?.data;
      let msg = "Registration failed. Please check your input.";
      if (data) {
        if (typeof data.username === "object") msg = `Username: ${(data.username as string[]).join(", ")}`;
        else if (typeof data.password === "object") msg = `Password: ${(data.password as string[]).join(", ")}`;
        else if (typeof data.detail === "string") msg = data.detail as string;
      }
      setErrorMessage(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0F172A] flex font-body">
      {/* Left Panel — Brand Illustration */}
      <div className="hidden lg:flex lg:w-5/12 xl:w-1/2 flex-col justify-center items-center p-12 relative overflow-hidden">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#0F172A] via-[#0F172A] to-[#0EA5E9]/20" />
        
        <div className="relative z-10 max-w-md text-center space-y-8">
          <div className="w-20 h-20 bg-[#0EA5E9] text-[#0F172A] rounded-3xl flex items-center justify-center mx-auto shadow-2xl shadow-[#0EA5E9]/30">
            <ShieldAlert className="w-10 h-10 stroke-[2.5]" />
          </div>
          
          <div>
            <h1 className="text-4xl font-extrabold text-white font-heading tracking-tight leading-tight">
              Office Leaks
            </h1>
            <p className="text-[#0EA5E9] text-sm font-bold uppercase tracking-[0.3em] mt-2">
              Encrypted · Anonymous · Transparent
            </p>
          </div>

          <p className="text-slate-300 text-sm leading-relaxed max-w-sm mx-auto">
            Join the verified anonymous corporate network where employees share workplace experiences, rate companies, and connect with peers — all protected by zero-trust encryption.
          </p>

          <div className="flex items-center justify-center gap-6 text-xs text-slate-400">
            <div className="flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-[#0EA5E9]" />
              <span>Zero-Trust</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-[#0EA5E9]" />
              <span>Encrypted</span>
            </div>
            <div className="flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5 text-[#0EA5E9]" />
              <span>Anonymous</span>
            </div>
          </div>
        </div>

        {/* Decorative circles */}
        <div className="absolute -bottom-32 -left-32 w-96 h-96 rounded-full bg-[#0EA5E9]/5 blur-3xl" />
        <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full bg-[#0EA5E9]/10 blur-2xl" />
      </div>

      {/* Right Panel — Auth Forms */}
      <div className="flex-1 flex items-center justify-center p-6 md:p-12 bg-[#F8FAFC] lg:rounded-l-[3rem] relative">
        {onClose && (
          <button
            onClick={onClose}
            className="absolute top-6 right-6 text-slate-400 hover:text-slate-700 flex items-center gap-1 text-xs font-bold font-heading cursor-pointer transition-colors"
          >
            <ChevronLeft className="w-4 h-4" /> Back to Feed
          </button>
        )}
        <div className="w-full max-w-md">
          {/* Mobile Brand */}
          <div className="lg:hidden text-center mb-8 mt-8">
            <div className="w-14 h-14 bg-[#0EA5E9] text-[#0F172A] rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-[#0EA5E9]/20 mb-3">
              <ShieldAlert className="w-7 h-7 stroke-[2.5]" />
            </div>
            <h1 className="text-2xl font-extrabold text-slate-800 font-heading">Office Leaks</h1>
            <p className="text-[10px] text-[#0EA5E9] font-bold uppercase tracking-[0.2em] mt-1">Encrypted · Anonymous</p>
          </div>

          {/* Tab Switcher */}
          <div className="flex bg-slate-100 rounded-2xl p-1 mb-6">
            <button
              onClick={() => { setActiveTab("signin"); setErrorMessage(""); setRegStep(1); }}
              className={`flex-1 py-2.5 text-xs font-bold font-heading rounded-xl transition-all cursor-pointer ${
                activeTab === "signin"
                  ? "bg-white text-slate-800 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setActiveTab("register"); setErrorMessage(""); }}
              className={`flex-1 py-2.5 text-xs font-bold font-heading rounded-xl transition-all cursor-pointer ${
                activeTab === "register"
                  ? "bg-white text-slate-800 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              Create Account
            </button>
          </div>

          {/* Error Message */}
          {errorMessage && (
            <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 p-3 rounded-xl text-xs font-medium mb-4">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-500" />
              <span>{errorMessage}</span>
            </div>
          )}

          {activeTab === "signin" ? (
            /* SIGN IN FORM */
            <form onSubmit={handleSignIn} className="space-y-4 text-xs">
              <div>
                <h2 className="text-xl font-extrabold text-slate-800 font-heading mb-1">Welcome back</h2>
                <p className="text-slate-400 text-xs mb-6">Sign in to access your encrypted workspace</p>
              </div>

              <div className="space-y-1.5">
                <label className="font-bold text-slate-700">Email</label>
                <div className="relative">
                  <UserIcon className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    required
                    placeholder="Enter your email address"
                    value={loginUsername}
                    onChange={(e) => setLoginUsername(e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-xl pl-10 pr-4 py-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0EA5E9]/50 focus:border-[#0EA5E9] transition-all"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="font-bold text-slate-700">Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    placeholder="Enter password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-xl pl-10 pr-12 py-3 text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0EA5E9]/50 focus:border-[#0EA5E9] transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className={`w-full py-3.5 rounded-xl font-extrabold text-white text-sm font-heading shadow-lg transition-all mt-4 ${
                  submitting
                    ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                    : "bg-[#0EA5E9] hover:bg-[#0EA5E9]/90 active:scale-[0.98] cursor-pointer shadow-[#0EA5E9]/25"
                }`}
              >
                {submitting ? "Signing In..." : "Sign In to Office Leaks"}
              </button>
            </form>
          ) : (
            /* REGISTER FORM — Multi-Step */
            <form onSubmit={handleRegister} className="space-y-4 text-xs">
              <div>
                <h2 className="text-xl font-extrabold text-slate-800 font-heading mb-1">
                  {regStep === 1 ? "Create your account" : "Complete your profile"}
                </h2>
                <p className="text-slate-400 text-xs mb-4">
                  {regStep === 1 ? "Step 1 of 2 — Basic information" : "Step 2 of 2 — Tell us about yourself"}
                </p>
                {/* Step indicator */}
                <div className="flex gap-2 mb-4">
                  <div className={`h-1 flex-1 rounded-full transition-all ${regStep >= 1 ? "bg-[#0EA5E9]" : "bg-slate-200"}`} />
                  <div className={`h-1 flex-1 rounded-full transition-all ${regStep >= 2 ? "bg-[#0EA5E9]" : "bg-slate-200"}`} />
                </div>
              </div>

              {regStep === 1 ? (
                /* Step 1: Basic Info */
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <label className="font-bold text-slate-700">First Name <span className="text-red-500">*</span></label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. Marwan"
                        value={regFirstName}
                        onChange={(e) => setRegFirstName(e.target.value)}
                        className="w-full bg-white border border-slate-200 rounded-xl px-3.5 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0EA5E9]/50 focus:border-[#0EA5E9]"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="font-bold text-slate-700">Last Name <span className="text-red-500">*</span></label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. Badr"
                        value={regLastName}
                        onChange={(e) => setRegLastName(e.target.value)}
                        className="w-full bg-white border border-slate-200 rounded-xl px-3.5 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0EA5E9]/50 focus:border-[#0EA5E9]"
                      />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-bold text-slate-700">Email <span className="text-red-500">*</span></label>
                    <div className="relative">
                      <UserIcon className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type="email"
                        required
                        placeholder="Enter your email address"
                        value={regUsername}
                        onChange={(e) => {
                          setRegUsername(e.target.value);
                          if (emailError) setEmailError("");
                        }}
                        onBlur={(e) => validateEmail(e.target.value)}
                        className={`w-full bg-white border rounded-xl pl-10 pr-4 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0EA5E9]/50 ${
                          emailError ? "border-red-500 focus:border-red-500" : "border-slate-200 focus:border-[#0EA5E9]"
                        }`}
                      />
                    </div>
                    {emailError && (
                      <p className="text-xs text-red-500 flex items-center gap-1 mt-1 font-medium">
                        <AlertCircle className="w-3.5 h-3.5" />
                        {emailError}
                      </p>
                    )}
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-bold text-slate-700">Password <span className="text-red-500">*</span></label>
                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                      <input
                        type={showPassword ? "text" : "password"}
                        required
                        placeholder="Set account password"
                        value={regPassword}
                        onChange={(e) => setRegPassword(e.target.value)}
                        className="w-full bg-white border border-slate-200 rounded-xl pl-10 pr-12 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0EA5E9]/50 focus:border-[#0EA5E9]"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div className="space-y-1.5">
                      <label className="font-bold text-slate-700 flex items-center gap-1">
                        <Calendar className="w-3 h-3 text-slate-400" /> Age
                      </label>
                      <input
                        type="number"
                        min={18}
                        max={100}
                        value={regAge}
                        onChange={(e) => setRegAge(parseInt(e.target.value) || 25)}
                        className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0EA5E9]/50"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="font-bold text-slate-700 flex items-center gap-1">
                        <Globe className="w-3 h-3 text-slate-400" /> Country
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. KSA"
                        value={regCountry}
                        onChange={(e) => setRegCountry(e.target.value)}
                        className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0EA5E9]/50"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="font-bold text-slate-700">Gender <span className="text-red-500">*</span></label>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => setRegGender("MALE")}
                          className={`flex-1 py-2.5 rounded-xl text-[11px] font-bold border transition-all cursor-pointer ${
                            regGender === "MALE"
                              ? "bg-[#0EA5E9] border-[#0EA5E9] text-white"
                              : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                          }`}
                        >
                          Male
                        </button>
                        <button
                          type="button"
                          onClick={() => setRegGender("FEMALE")}
                          className={`flex-1 py-2.5 rounded-xl text-[11px] font-bold border transition-all cursor-pointer ${
                            regGender === "FEMALE"
                              ? "bg-[#0EA5E9] border-[#0EA5E9] text-white"
                              : "bg-white border-slate-200 text-slate-600 hover:border-slate-300"
                          }`}
                        >
                          Female
                        </button>
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      if (!regUsername.trim() || !regFirstName.trim() || !regLastName.trim() || !regPassword.trim()) {
                        setErrorMessage("Please fill in all required fields before continuing.");
                        return;
                      }
                      if (!validateEmail(regUsername)) {
                        setErrorMessage("Please enter a valid email address.");
                        return;
                      }
                      setErrorMessage("");
                      setRegStep(2);
                    }}
                    className="w-full py-3 rounded-xl font-extrabold text-white text-xs font-heading shadow-md bg-[#0F172A] hover:bg-slate-800 active:scale-[0.98] cursor-pointer transition-all mt-2 flex items-center justify-center gap-2"
                  >
                    Continue <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                /* Step 2: Profile Details */
                <div className="space-y-3">
                  <div className="space-y-1.5">
                    <label className="font-bold text-slate-700 flex items-center gap-1">
                      <Building className="w-3 h-3 text-slate-400" /> Current Company
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Google, Aramco, STC..."
                      value={regCompany}
                      onChange={(e) => setRegCompany(e.target.value)}
                      className="w-full bg-white border border-slate-200 rounded-xl px-3.5 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0EA5E9]/50 focus:border-[#0EA5E9]"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-bold text-slate-700 flex items-center gap-1">
                      <FileText className="w-3 h-3 text-slate-400" /> About You
                    </label>
                    <textarea
                      placeholder="Tell us a bit about yourself, your expertise, interests..."
                      value={regAbout}
                      onChange={(e) => setRegAbout(e.target.value)}
                      rows={3}
                      maxLength={1000}
                      className="w-full bg-white border border-slate-200 rounded-xl px-3.5 py-2.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0EA5E9]/50 focus:border-[#0EA5E9] resize-none"
                    />
                    <p className="text-[10px] text-slate-400 text-right">{regAbout.length}/1000</p>
                  </div>

                  {/* Preview avatar */}
                  <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl border border-slate-100">
                    <img
                      src={regGender === "FEMALE" ? femaleAvatar : maleAvatar}
                      alt="Default avatar"
                      className="w-12 h-12 rounded-xl border border-slate-200 object-cover"
                    />
                    <div>
                      <p className="text-[11px] text-slate-500">Your default avatar</p>
                      <p className="text-[10px] text-slate-400 mt-0.5">
                        You can upload a custom photo from your profile after registration.
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-3 mt-2">
                    <button
                      type="button"
                      onClick={() => setRegStep(1)}
                      className="flex-1 py-3 rounded-xl font-bold text-slate-600 text-xs font-heading border border-slate-200 bg-white hover:bg-slate-50 cursor-pointer transition-all flex items-center justify-center gap-1"
                    >
                      <ChevronLeft className="w-4 h-4" /> Back
                    </button>
                    <button
                      type="submit"
                      disabled={submitting}
                      className={`flex-1 py-3 rounded-xl font-extrabold text-white text-xs font-heading shadow-md transition-all ${
                        submitting
                          ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                          : "bg-[#0EA5E9] hover:bg-[#0EA5E9]/90 active:scale-[0.98] cursor-pointer shadow-[#0EA5E9]/25"
                      }`}
                    >
                      {submitting ? "Creating Account..." : "Create Account"}
                    </button>
                  </div>
                </div>
              )}
            </form>
          )}

          {/* Security badge */}
          <div className="bg-white border border-slate-100 rounded-xl p-3 text-[11px] text-slate-500 flex items-center gap-2 mt-6 shadow-sm">
            <Shield className="w-4 h-4 text-[#0EA5E9] flex-shrink-0" />
            <p>Your real name is stored securely. All leaks and reviews can be published completely anonymously.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
