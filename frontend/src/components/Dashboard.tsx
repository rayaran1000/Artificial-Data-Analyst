import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  LayoutDashboard, 
  FileText,
  ArrowRight,
  Eraser,
  Database,
  Settings2
} from "lucide-react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface DashboardProps {
    darkMode: boolean;
    toggleDarkMode: () => void;
  }

const Dashboard: React.FC<DashboardProps> = ({ darkMode,  }) => {
  const [username, setUsername] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    fetchUserData()
  }, [])

  const fetchUserData = async () => {
    try {
      const response = await fetch('http://localhost:8000/user/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setUsername(data.name)
      } else {
        console.error('Failed to fetch user data')
      }
    } catch (error) {
      console.error('Error fetching user data:', error)
    }
  }

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-900'}`}>
      <main className="flex-grow container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold mb-2">Welcome back, {username}!</h1>
          <p className="text-xl">Here's an overview of your dashboard.</p>
        </motion.div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 mb-8">
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Data Control
              </CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground mb-4">
                Manage your data sources and connections
              </p>
              <Button className="w-full" onClick={() => navigate('/datacontrol')}>
                Manage Data <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Data Summarizer
              </CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground mb-4">
                Summarize your data for better understanding
              </p>
              <Button className="w-full" onClick={() => navigate('/datasummarizer')}>
                Summarize Data <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Data Cleaner
              </CardTitle>
              <Eraser className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground mb-4">
                Clean your data and make it more suitable for your analysis
              </p>
              <Button className="w-full" onClick={() => navigate('/datacleaner')}>
                Cleaning Data <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Data Visualizer
              </CardTitle>
              <LayoutDashboard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground mb-4">
                Visualize your data for analytical understanding
              </p>
              <Button className="w-full" onClick={() => navigate('/visualize')}>
                Visualize Data <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Settings
              </CardTitle>
              <Settings2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground mb-4">
                Modify & Manage your Settings
              </p>
              <Button className="w-full" onClick={() => navigate('/settings')}>
                Settings <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

export default Dashboard;