import React, { useState } from "react";
import { BarChart2, PieChart, TrendingUp, Activity, Plus, X, ArrowLeft, ArrowDown, Pencil} from 'lucide-react';
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { useNavigate } from 'react-router-dom'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface DataVisualizerProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

interface Goal {
  id: number;
  question: string;
  icon: React.ReactNode;
}

const availableIcons = [
  <TrendingUp className="h-5 w-5" />,
  <PieChart className="h-5 w-5" />,
  <BarChart2 className="h-5 w-5" />,
  <Activity className="h-5 w-5" />
];

const DataVisualizer: React.FC<DataVisualizerProps> = ({ darkMode }) => {
  const [goalCount, setGoalCount] = useState(5);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [visualization, setVisualization] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showChatbox, setShowChatbox] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [visualizationOption, setVisualizationOption] = useState("matplotlib");
  const [visualizationCount, setVisualizationCount] = useState(1);
  const [visualizationTitles, setVisualizationTitles] = useState<string[]>([]);
  const [selectedVisualizationTitle, setSelectedVisualizationTitle] = useState<string | null>(null);
  const navigate = useNavigate()

  const fetchGoalsFromBackend = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch("http://localhost:8000/visualize/goalgenerator", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json" ,
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ goalCount }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch goals from the backend.");
      }

      const data = await response.json();
      const generatedGoals = data.goals.map((goal: any, index: number) => ({
        id: goal.id,
        question: goal.question,
        icon: availableIcons[index % availableIcons.length],
      }));

      setGoals(generatedGoals);
    } catch (error) {
      console.error("Error fetching goals:", error);
      alert("Failed to generate goals. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoalSelect = (goal: Goal) => {
    setSelectedGoal(goal);
    setVisualization(null);
    setSelectedVisualizationTitle(null);
    setVisualizationTitles([]);
  };

  const handleVisualizationRequest = async () => {
    if (!selectedGoal) {
      alert("Please select a goal first");
      return;
    }
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch("http://localhost:8000/visualize/visualization-titles", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          visualization_count : visualizationCount
        }),
      });

      if (!response.ok) throw new Error("Failed to fetch visualizations from backend");
      
      const data = await response.json();
      setVisualizationTitles(data.visualizationTitles);
    } catch (error) {
      console.error("Error fetching visualizations:", error);
      alert("Failed to fetch visualizations. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVisualizationTitleSelect = async (title: string) => {
    if (!selectedGoal) {
      alert("Please select a goal first");
      return;
    }
    setSelectedVisualizationTitle(title);
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch("http://localhost:8000/visualize/visualizations", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ 
          goal: selectedGoal,
          visualization_option: visualizationOption,
          visualization_count: visualizationCount,
          visualization_title: title
        }),
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Failed to fetch visualization: ${errorData}`);
      }
      
      const data = await response.json();

      if (data.visualization?.raster) {
        const imageBase64 = `data:${data.visualization.type || 'image/png'};base64,${data.visualization.raster}`
        setVisualization(imageBase64);
        localStorage.setItem("savedVisualization",imageBase64)
      } else {
        throw new Error("No valid image data found in the response");
      }
    } catch (error) {
      console.error("Error fetching visualization:", error);
    } finally {
      setIsLoading(false);
    }
  };

// Add this component to display the visualization
  const VisualizationDisplay = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center p-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      );
    }
    
    if (visualization) {
      return (
        <div className="w-full max-w-4xl mx-auto p-4">
          <div className="relative bg-white rounded-lg shadow-lg overflow-hidden">
            <img 
              src={visualization} 
              alt="Data Visualization" 
              className="w-full h-full object-contain"
              style={{
                backgroundColor: 'transparent',
                display: 'block',  // Prevents unwanted spacing
                margin: '0 auto'   // Centers the image
              }}
            />
          </div>
        </div>
      );
    }
    
    return null;
  };

  const handleAddGoal = async () => {
    if (chatInput.trim() === "") {
      alert("Please enter a goal description");
      return;
    }
    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch("http://localhost:8000/visualize/goaladdition", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ description: chatInput, goalCount: goalCount }),
      });

      if (!response.ok) {
        throw new Error("Failed to add goal.");
      }

      const newGoal = await response.json();
      setGoals([...goals, {
        id: newGoal.id,
        question: newGoal.question,
        icon: availableIcons[goals.length % availableIcons.length],
      }]);
      setChatInput("");
      setShowChatbox(false);
    } catch (error) {
      console.error("Error adding goal:", error);
      alert("Failed to add goal. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToTitles = () => {
    setSelectedVisualizationTitle(null);
    setVisualization(null);
  };

  const handleDownload = () => {
    if (!visualization) {
      alert("No visualization available to download.");
      return;
    }
  
    // Create a link element
    const link = document.createElement("a");
    
    // Set the download attribute and the image source
    link.download = `${selectedVisualizationTitle || "visualization"}.png`;
    link.href = visualization;
    
    // Programmatically click the link to trigger the download
    link.click();
  };

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? "bg-gray-800 text-white" : "bg-gray-100 text-gray-900"}`}>
      <main className="flex-grow container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center justify-between mb-8"
        >
          <div className="flex items-center">
            <h1 className="text-3xl font-bold">Dynamic Data Visualizer</h1>
          </div>
        </motion.div>

        <div className="grid grid-cols-12 gap-6">
          {/* Goals Sidebar */}
          <Card className="col-span-5 h-[600px] overflow-y-auto">
            <CardContent className="p-4">
              <h2 className="text-xl font-semibold mb-4">Set Number of Goals</h2>
              <Slider
                value={[goalCount]}
                onValueChange={(value) => setGoalCount(value[0])}
                min={1}
                max={10}
                step={1}
                className="w-full"
              />
              <p className="text-center text-sm mt-2">Number of Goals: {goalCount}</p>
              <Button
                className="w-full mt-4"
                onClick={fetchGoalsFromBackend}
                disabled={isLoading}
              >
                {isLoading ? "Generating..." : "Generate"}
              </Button>

              <h2 className="text-xl font-semibold mt-4 mb-2">Goals</h2>
              <div className="space-y-2">
                {goals.map((goal) => (
                  <Button
                    key={goal.id}
                    variant={selectedGoal?.id === goal.id ? "default" : "outline"}
                    className={`w-full justify-start ${
                      selectedGoal?.id === goal.id ? "bg-blue-500 text-white" : ""
                    }`}
                    onClick={() => handleGoalSelect(goal)}
                  >
                    {goal.icon}
                    <span className="ml-2">{goal.question}</span>
                  </Button>
                ))}
              </div>
              <Button
                className="w-full mt-4"
                onClick={() => setShowChatbox(!showChatbox)}
              >
                {showChatbox ? <X className="mr-2" /> : <Plus className="mr-2" />}
                {showChatbox ? "Close" : "Add Goal"}
              </Button>
              {showChatbox && (
                <div className="mt-4">
                  <Textarea
                    placeholder="Describe your goal..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    className="w-full mb-2"
                  />
                  <Button onClick={handleAddGoal} disabled={isLoading} className="w-full">
                    {isLoading ? "Adding..." : "Add Goal"}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
          {/* Main Visualization Area */}
          <div className="col-span-7 space-y-6">
            <Card className="h-[700px]">
              <CardContent className="p-4">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold">Visualization</h2>
                  <div className="flex items-center space-x-4">
                    <Select value={visualizationOption} onValueChange={setVisualizationOption}>
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Select visualization" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="matplotlib">Matplotlib</SelectItem>
                        <SelectItem value="seaborn">Seaborn</SelectItem>
                      </SelectContent>
                    </Select>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm">Visualizations:</span>
                      <Slider
                        value={[visualizationCount]}
                        onValueChange={(value) => setVisualizationCount(value[0])}
                        min={1}
                        max={10}
                        step={1}
                        className="w-[100px]"
                      />
                      <span className="text-sm">{visualizationCount}</span>
                    </div>
                    <Button
                      onClick={handleVisualizationRequest}
                      disabled={!selectedGoal || isLoading}
                    >
                      Visualize
                    </Button>
                  </div>
                </div>
                {selectedGoal && visualizationTitles.length > 0 && !selectedVisualizationTitle && (
                  <div className="h-[800px] overflow-y-auto">
                    <h3 className="text-lg font-semibold mb-2">Available Visualizations</h3>
                    <div className="space-y-2">
                      {visualizationTitles.map((title, index) => (
                        <Button
                          key={index}
                          variant="outline"
                          className="w-full justify-start"
                          onClick={() => handleVisualizationTitleSelect(title)}
                        >
                          {title}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
                {selectedVisualizationTitle && (
                  <div className="h-[400px] flex flex-col">
                    <Button
                      variant="outline"
                      className="self-start mb-2"
                      onClick={handleBackToTitles}
                    >
                      <ArrowLeft className="mr-2 h-4 w-4" />
                      Back to Titles
                    </Button>
                    <Button
                      variant="outline"
                      className="self-start ml-auto mb-2"
                      onClick={() => navigate('/visualize/edit')}
                    >
                      <Pencil className="mr-2 h-4 w-4" />
                      Edit & Enhance
                    </Button>
                    <Button
                      variant="outline"
                      className="self-start ml-auto mb-2"
                      onClick={handleDownload}
                    >
                      <ArrowDown className="mr-2 h-4 w-4" />
                      Download
                    </Button>
                    <VisualizationDisplay />
                  </div>
                )}
                {!selectedGoal && (
                  <div className="h-[400px] flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg">
                    Select a goal to view available visualizations
                  </div>
                )}
                {selectedGoal && visualizationTitles.length === 0 && (
                  <div className="h-[400px] flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg">
                    Click "Visualize" to fetch available visualizations
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DataVisualizer;