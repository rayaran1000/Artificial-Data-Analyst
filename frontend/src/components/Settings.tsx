import React, { useState, useEffect } from 'react'
import { Settings as SettingsIcon, User, Lock, Edit2, Eye, EyeOff } from "lucide-react"
import { motion } from "framer-motion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Toast from './Toast'

interface UserProfile {
  name: string
  email: string
}

interface ToastState {
  message: string
  type: 'success' | 'error'
}

interface SettingsProps {
    darkMode: boolean;
    toggleDarkMode: () => void;
  }

const Settings: React.FC<SettingsProps> = ({ darkMode }) => {
    const [profile, setProfile] = useState<UserProfile>({ name: '', email: '' })
    const [editName, setEditName] = useState(false)
    const [editEmail, setEditEmail] = useState(false)
    const [newName, setNewName] = useState('')
    const [newEmail, setNewEmail] = useState('')
    const [newPassword, setNewPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [showNewPassword, setShowNewPassword] = useState(false)
    const [showConfirmPassword, setShowConfirmPassword] = useState(false)
    const [toast, setToast] = useState<ToastState | null>(null)

    useEffect(() => {
        fetchUserProfile()
      }, [])
    
      const fetchUserProfile = async () => {
        try {
          const response = await fetch('http://localhost:8000/user/profile', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          })
          if (response.ok) {
            const data = await response.json()
            setProfile(data)
            setNewName(data.name)
            setNewEmail(data.email)
          } else {
            console.error('Failed to fetch user profile')
          }
        } catch (error) {
          console.error('Error fetching user profile:', error)
        }
      }
    
      const showToast = (message: string, type: 'success' | 'error') => {
        setToast({ message, type })
      }
    
      const handleUpdateName = async () => {
        try {
          const response = await fetch('http://localhost:8000/user/update-name', {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ name: newName })
          })
          if (response.ok) {
            setProfile({ ...profile, name: newName })
            setEditName(false)
            showToast("Your name has been successfully updated.", "success")
          } else {
            showToast("Failed to update name. Please try again.", "error")
          }
        } catch (error) {
          console.error('Error updating name:', error)
          showToast("An error occurred while updating your name.", "error")
        }
      }
    
      const handleUpdateEmail = async () => {
        try {
          const response = await fetch('http://localhost:8000/user/update-email', {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ email: newEmail })
          })
          if (response.ok) {
            setProfile({ ...profile, email: newEmail })
            setEditEmail(false)
            showToast("Your email has been successfully updated.", "success")
          } else {
            showToast("Failed to update email. Please try again.", "error")
          }
        } catch (error) {
          console.error('Error updating email:', error)
          showToast("An error occurred while updating your email.", "error")
        }
      }
    
      const handlePasswordChange = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        if (newPassword !== confirmPassword) {
          showToast("New password and confirm password do not match.", "error")
          return
        }
        try {
          const response = await fetch('http://localhost:8000/user/change-password', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ newPassword })
          })
          if (response.ok) {
            showToast("Your password has been successfully changed.", "success")
            setNewPassword('')
            setConfirmPassword('')
          } else {
            showToast("Failed to change password. Please try again.", "error")
          }
        } catch (error) {
          console.error('Error changing password:', error)
          showToast("An error occurred while changing your password.", "error")
        }
      }
    
      return (
        <div className={`min-h-screen flex flex-col ${darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-900'}`}>
          <main className="flex-grow container mx-auto px-4 py-8">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center mb-8"
            >
              <SettingsIcon className="mr-2 h-6 w-6" />
              <h1 className="text-3xl font-bold">Settings</h1>
            </motion.div>
    
            <div className="grid gap-8">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <User className="mr-2 h-5 w-5" />
                    Profile Information
                  </CardTitle>
                  <CardDescription>View and update your account profile</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="name">Name</Label>
                      {editName ? (
                        <Input
                          id="name"
                          value={newName}
                          onChange={(e) => setNewName(e.target.value)}
                          className="mt-1"
                        />
                      ) : (
                        <p className="mt-1">{profile.name}</p>
                      )}
                    </div>
                    {editName ? (
                      <div>
                        <Button onClick={handleUpdateName} className="mr-2">Save</Button>
                        <Button variant="outline" onClick={() => setEditName(false)}>Cancel</Button>
                      </div>
                    ) : (
                      <Button onClick={() => setEditName(true)}>
                        <Edit2 className="h-4 w-4 mr-2" />
                        Edit
                      </Button>
                    )}
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="email">Email</Label>
                      {editEmail ? (
                        <Input
                          id="email"
                          type="email"
                          value={newEmail}
                          onChange={(e) => setNewEmail(e.target.value)}
                          className="mt-1"
                        />
                      ) : (
                        <p className="mt-1">{profile.email}</p>
                      )}
                    </div>
                    {editEmail ? (
                      <div>
                        <Button onClick={handleUpdateEmail} className="mr-2">Save</Button>
                        <Button variant="outline" onClick={() => setEditEmail(false)}>Cancel</Button>
                      </div>
                    ) : (
                      <Button onClick={() => setEditEmail(true)}>
                        <Edit2 className="h-4 w-4 mr-2" />
                        Edit
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
    
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Lock className="mr-2 h-5 w-5" />
                    Change Password
                  </CardTitle>
                  <CardDescription>Update your account password</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handlePasswordChange} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="newPassword">New Password</Label>
                      <div className="relative">
                        <Input
                          id="newPassword"
                          type={showNewPassword ? "text" : "password"}
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                          onClick={() => setShowNewPassword(!showNewPassword)}
                        >
                          {showNewPassword ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="confirmPassword">Confirm New Password</Label>
                      <div className="relative">
                        <Input
                          id="confirmPassword"
                          type={showConfirmPassword ? "text" : "password"}
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        >
                          {showConfirmPassword ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </div>
                    <Button type="submit">Change Password</Button>
                  </form>
                </CardContent>
              </Card>
            </div>
          </main>
          {toast && (
            <Toast
              message={toast.message}
              type={toast.type}
              onClose={() => setToast(null)}
            />
          )}
        </div>
      )
    }

export default Settings;