"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { LogIn, Building, GraduationCap, MonitorPlay } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useRouter } from "next/navigation";
import axios from "axios";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    
    try {
      const url = "http://localhost:8000/api/v1/auth/login";
      const response = await axios.post(url, {
        email,
        password
      });

      if (response.data.status === "success") {
        // Save user data to localStorage
        localStorage.setItem("user", JSON.stringify(response.data.user));
        
        // Redirect logic based on role
        if (response.data.user.role === "supervisor") {
          router.push("/supervisor");
        } else {
          // Placeholder for other roles
          router.push("/supervisor"); 
        }
      } else {
        setError(response.data.message || "Giriş başarısız.");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Sunucu bağlantı hatası.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center gap-3 mb-8">
          <div className="bg-primary/10 p-3 rounded-2xl glass shadow-inner shadow-primary/20">
            <MonitorPlay className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-4xl font-extrabold tracking-tighter bg-gradient-to-br from-slate-900 to-slate-500 dark:from-white dark:to-slate-400 bg-clip-text text-transparent">
            Akıllı Atölye
          </h1>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="w-full max-w-md relative z-10"
      >
        <Card className="w-full backdrop-blur-2xl">
          <CardHeader>
            <CardTitle className="text-center text-3xl">Sisteme Giriş</CardTitle>
            <CardDescription className="text-center text-base">
              Öğrenci, Okul veya Supervisor olarak devam edin
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-6">
              <div className="space-y-4">
                {error && (
                  <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-sm text-center font-medium">
                    {error}
                  </div>
                )}
                <Input
                  type="email"
                  placeholder="E-posta adresiniz (Örn: admin@akilliatolye.com)"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
                <Input
                  type="password"
                  placeholder="Şifreniz"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              <div className="flex justify-between items-center text-sm px-1">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="rounded border-slate-300 text-primary focus:ring-primary" />
                  <span className="text-slate-600 dark:text-slate-400">Beni hatırla</span>
                </label>
                <a href="#" className="text-primary hover:text-primary-hover hover:underline transition-colors font-medium">Şifremi unuttum</a>
              </div>

              <Button type="submit" className="w-full h-12 text-lg group" disabled={isLoading}>
                {isLoading ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                  >
                    <LogIn className="w-5 h-5" />
                  </motion.div>
                ) : (
                  <div className="flex items-center gap-2">
                    Giriş Yap
                    <LogIn className="w-5 h-5 opacity-70 group-hover:opacity-100 transition-opacity" />
                  </div>
                )}
              </Button>
            </form>

            <div className="mt-8 grid grid-cols-3 gap-3">
              <div className="flex flex-col items-center justify-center p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/20 dark:bg-black/20 hover:bg-white/40 dark:hover:bg-slate-800/40 cursor-pointer transition-colors group">
                <GraduationCap className="w-6 h-6 mb-1 text-emerald-500 group-hover:scale-110 transition-transform" />
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Öğrenci</span>
              </div>
              <div className="flex flex-col items-center justify-center p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/20 dark:bg-black/20 hover:bg-white/40 dark:hover:bg-slate-800/40 cursor-pointer transition-colors group">
                <Building className="w-6 h-6 mb-1 text-blue-500 group-hover:scale-110 transition-transform" />
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Kurum</span>
              </div>
              <div className="flex flex-col items-center justify-center p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/20 dark:bg-black/20 hover:bg-white/40 dark:hover:bg-slate-800/40 cursor-pointer transition-colors group">
                <MonitorPlay className="w-6 h-6 mb-1 text-purple-500 group-hover:scale-110 transition-transform" />
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Admin</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
