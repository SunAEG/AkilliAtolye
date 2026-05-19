"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Users, LayoutDashboard, Plus, ShieldCheck, MonitorPlay, LogOut } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { useRouter } from "next/navigation";
import axios from "axios";

// Mock Data
const MOCK_ROLES = [
  { id: 1, name: "Öğrenci Grubu", users: 120, screens: 2 },
  { id: 2, name: "Okul Yönetimi", users: 5, screens: 5 },
  { id: 3, name: "İşletme Yetkilileri", users: 12, screens: 3 },
];

export default function SupervisorDashboard() {
  const router = useRouter();
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState<any>(null);
  
  // Permissions State (Matches JSONB logic in backend)
  const [perms, setPerms] = useState({ create: false, read: true, update: false, delete: false });

  const openAssignModal = (role: any) => {
    setSelectedRole(role);
    setIsAssignModalOpen(true);
  };

  const handleAssign = async () => {
    try {
      // Varsayılan olarak ekran ID'sini 1 (Örn: Yönetim Ekranı) yapalım.
      const screenId = 1;
      const url = `http://localhost:8000/api/v1/supervisor/roles/${selectedRole.id}/assign-screen/${screenId}`;
      await axios.post(url, {
        create: perms.create,
        read: perms.read,
        update: perms.update,
        delete: perms.delete
      });
      alert(`${selectedRole.name} için yetkilendirme başarıyla tamamlandı!`);
    } catch (err: any) {
      alert("Hata: " + (err.response?.data?.detail || "Sunucuya bağlanılamadı."));
    } finally {
      setIsAssignModalOpen(false);
    }
  };

  return (
    <div className="min-h-screen p-6 md:p-12 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-center justify-between gap-4"
      >
        <div className="flex items-center gap-4">
          <div className="p-3 bg-primary/10 rounded-2xl glass shadow-inner shadow-primary/20">
            <ShieldCheck className="w-8 h-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">Supervisor Paneli</h1>
            <p className="text-slate-500 dark:text-slate-400 font-medium">Rol, ekran ve yetki yönetimi merkezi</p>
          </div>
        </div>
        <Button variant="ghost" onClick={() => router.push("/login")}>
          <LogOut className="w-4 h-4 mr-2" />
          Çıkış Yap
        </Button>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { title: "Toplam Kullanıcı", value: "137", icon: Users, color: "text-blue-500" },
          { title: "Aktif Gruplar", value: "3", icon: ShieldCheck, color: "text-emerald-500" },
          { title: "Kayıtlı Ekranlar", value: "12", icon: LayoutDashboard, color: "text-purple-500" },
        ].map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="hover:shadow-xl transition-shadow duration-300">
              <CardContent className="p-6 flex items-center gap-4">
                <div className={`p-4 rounded-xl bg-slate-100 dark:bg-slate-800 ${stat.color}`}>
                  <stat.icon className="w-7 h-7" />
                </div>
                <div>
                  <p className="text-sm text-slate-500 font-semibold uppercase tracking-wider">{stat.title}</p>
                  <p className="text-4xl font-extrabold">{stat.value}</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Roles List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card>
          <CardHeader className="flex flex-row items-center justify-between border-b border-slate-200/50 dark:border-slate-800/50">
            <div>
              <CardTitle>Grup ve Rol Yönetimi</CardTitle>
              <CardDescription>Sistemdeki tüm grupların CRUD yetkilerini buradan ayarlayın.</CardDescription>
            </div>
            <Button size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Yeni Grup
            </Button>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {MOCK_ROLES.map((role) => (
                <div key={role.id} className="flex flex-col md:flex-row md:items-center justify-between p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 hover:bg-white dark:hover:bg-slate-800 transition-all shadow-sm hover:shadow-md">
                  <div className="flex items-center gap-4 mb-4 md:mb-0">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-xl">
                      {role.name.charAt(0)}
                    </div>
                    <div>
                      <h4 className="font-bold text-lg">{role.name}</h4>
                      <p className="text-sm text-slate-500 font-medium">{role.users} Kullanıcı • {role.screens} Ekran Atanmış</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <Button variant="outline" size="sm">Düzenle</Button>
                    <Button variant="primary" size="sm" onClick={() => openAssignModal(role)}>
                      <MonitorPlay className="w-4 h-4 mr-2" />
                      Ekran Ata & Yetkilendir
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Assignment Modal */}
      <Modal 
        isOpen={isAssignModalOpen} 
        onClose={() => setIsAssignModalOpen(false)}
        title="Dinamik Ekran Atama"
      >
        <div className="space-y-6">
          <p className="text-slate-600 dark:text-slate-300">
            <strong>{selectedRole?.name}</strong> için yeni bir ekran ve bu ekran üzerindeki CRUD (Oluşturma, Okuma, Güncelleme, Silme) izinlerini ayarlıyorsunuz.
          </p>

          <div className="space-y-4">
            <h4 className="font-bold text-sm text-slate-500 uppercase tracking-wider">İzinler (JSONB Verisi)</h4>
            <div className="grid grid-cols-2 gap-3">
              {[
                { id: "read", label: "Okuma (Read)" },
                { id: "create", label: "Oluşturma (Create)" },
                { id: "update", label: "Güncelleme (Update)" },
                { id: "delete", label: "Silme (Delete)" },
              ].map((perm) => (
                <label key={perm.id} className="flex items-center gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 cursor-pointer transition-colors">
                  <input 
                    type="checkbox" 
                    checked={perms[perm.id as keyof typeof perms]}
                    onChange={(e) => setPerms({...perms, [perm.id]: e.target.checked})}
                    className="w-5 h-5 text-primary rounded border-slate-300 focus:ring-primary focus:ring-offset-0" 
                  />
                  <span className="font-semibold">{perm.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="pt-6 flex justify-end gap-3 border-t border-slate-200 dark:border-slate-800">
            <Button variant="ghost" onClick={() => setIsAssignModalOpen(false)}>İptal</Button>
            <Button onClick={handleAssign}>
              <ShieldCheck className="w-5 h-5 mr-2" />
              Yetkileri Kaydet
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
