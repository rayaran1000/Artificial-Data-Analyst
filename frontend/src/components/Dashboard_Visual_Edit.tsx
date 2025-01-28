import { useState, useEffect } from 'react';
import { ArrowLeft, MessageSquare, FileText, PenToolIcon as Tool, ArrowDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";

interface VisualizationEditPageProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

type evalu = {
  dimension: string;
  score: string;
  rationale: string;
}

export default function VisualizationEditPage({ darkMode,  }: VisualizationEditPageProps) {
  const navigate = useNavigate();
  const [visualization, setVisualization] = useState<string | null>(localStorage.getItem("savedVisualization") || null);
  const [nlpInput, setNlpInput] = useState('');
  const [explanation, setExplanation] = useState('');
  const [evaluation, setEvaluation] = useState<evalu[]>([]);
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const savedImage = localStorage.getItem("savedVisualization");
    if (savedImage) {
      setVisualization(savedImage);
    }
  }, []);

  const handleUndoEdit = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/visualize/undo-edit', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
      });
      if (!response.ok) throw new Error('Failed to edit visualization');

      const data = await response.json();

      if (data.visualization?.raster) {
        const imageBase64 = `data:${data.visualization.type || 'image/png'};base64,${data.visualization.raster}`
        setVisualization(imageBase64);
      } else {
        throw new Error("No valid image data found in the response");
      }
    } catch (error) {
      console.error('Error editing visualization:', error);
      alert('Failed to edit visualization. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNaturalLanguageEditing = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/visualize/edit-visualization', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ nlpInput })
      });
      if (!response.ok) throw new Error('Failed to edit visualization');

      const data = await response.json();

      if (data.visualization?.raster) {
        const imageBase64 = `data:${data.visualization.type || 'image/png'};base64,${data.visualization.raster}`
        setVisualization(imageBase64);
      } else {
        throw new Error("No valid image data found in the response");
      }
    } catch (error) {
      console.error('Error editing visualization:', error);
      alert('Failed to edit visualization. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVisualizationExplanation = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/visualize/explain-visualization', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
      });

      if (!response.ok) throw new Error('Failed to fetch explanation');

      const data = await response.json();
      setExplanation(data['explanation']);

    } catch (error) {
      console.error('Error fetching explanation:', error);
      alert('Failed to fetch explanation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEvaluateAndRepair = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/visualize/evaluate-visualization', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
      });

      if (!response.ok) throw new Error('Failed to evaluate and repair');

      const data = await response.json();
      setEvaluation(data.evaluation);
    } catch (error) {
      console.error('Error evaluating and repairing:', error);
      alert('Failed to evaluate and repair. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Copied to clipboard!');
    }, (err) => {
      console.error('Could not copy text: ', err);
    });
  };

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

  const clearDatabaseAndNavigate = async () => {
    try {
      // Send a POST request to the backend to clear the database
      const response = await fetch('http://localhost:8000/visualize/clear-db', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to clear the database');
      }

      // Navigate back to the previous page
      navigate(-1);
    } catch (error) {
      console.error('Error clearing the database:', error);
      alert('An error occurred while clearing the database.');
    }
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
            <Button
              variant="ghost"
              onClick={clearDatabaseAndNavigate}
              className="mr-4"
            >
              <ArrowLeft className="h-6 w-6" />
            </Button>
            <h1 className="text-3xl font-bold">Edit Visualization</h1>
          </div>
        </motion.div>
        <div className="grid grid-cols-12 gap-6">
          {/* Main Visualization Area */}
          <Card className="col-span-8 h-[700px]">
            <CardContent className="p-4">
              <div className="flex justify-between">
                <Button
                  variant="ghost"
                  onClick={handleUndoEdit}
                  className="mr-4"
                >
                  <ArrowLeft className="h-3 w-3 mr-2" />
                  Undo Visual Edit
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => {
                    if (visualization) {
                      const link = document.createElement("a");
                      link.download = "visualization.png";
                      link.href = visualization;
                      link.click();
                    }
                  }}
                >
                  <ArrowDown className="h-3 w-3 mr-2" />
                  Download
                </Button>
              </div>
              <VisualizationDisplay/>
            </CardContent>
          </Card>

          {/* Editing Options */}
          <div className="col-span-4 space-y-4">
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => setActiveSection(activeSection === 'nlp' ? null : 'nlp')}
            >
              <MessageSquare className="mr-2 h-4 w-4" />
              Natural Language Editing
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => {
                if (activeSection === 'explanation') {
                  setActiveSection(null);
                } else {
                  setActiveSection('explanation');
                  handleVisualizationExplanation();
                }
              }}
            >
              <FileText className="mr-2 h-4 w-4" />
              Visualization Explanation
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => {
                if (activeSection === 'evaluate') {
                  setActiveSection(null);
                } else {
                  setActiveSection('evaluate');
                  handleEvaluateAndRepair();
                }
              }}
            >
              <Tool className="mr-2 h-4 w-4" />
              Evaluate & Repair
            </Button>

            {/* Active Section Content */}
            {activeSection && (
              <Card className="mt-4">
                <CardContent className="p-4">
                  {activeSection === 'nlp' && (
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Natural Language Editing</h3>
                      <Textarea
                        placeholder="Describe how you want to edit the visualization..."
                        value={nlpInput}
                        onChange={(e) => setNlpInput(e.target.value)}
                        className="w-full h-32"
                      />
                      <Button onClick={handleNaturalLanguageEditing} disabled={isLoading}>
                        {isLoading ? 'Editing...' : 'Apply'}
                      </Button>
                    </div>
                  )}
                  {activeSection === 'explanation' && (
                    <ScrollArea className="h-[200px]">
                      <h3 className="text-lg font-semibold mb-2">Visualization Explanation</h3>
                      {isLoading ? (
                        <p>Loading explanation...</p>
                      ) : (
                        <p>{explanation || 'No explanation available.'}</p>
                      )}
                    </ScrollArea>
                  )}
                  {activeSection === 'evaluate' && (
                    <ScrollArea className="h-[200px]">
                      <h3 className="text-lg font-semibold mb-2">Evaluation & Repair</h3>
                      <p className="mt-2 text-sm text-white-500">**********************************</p>
                      {isLoading ? (
                        <p>Evaluating...</p>
                      ) : (
                        <div>
                          {evaluation && evaluation.length > 0 ? (
                            <div className="mt-4">
                              {evaluation.map((evalu, index) => (
                                <div key={index} className="evaluation-group mb-4">
                                  <ul>
                                    <li className="font-bold">
                                      {evalu.dimension} - {evalu.score}
                                    </li>
                                  </ul>
                                  <p className="mt-2">{evalu.rationale}</p>
                                  <p className="mt-2 text-sm text-gray-500">**********************************</p>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    className="mt-2"
                                    onClick={() =>
                                      copyToClipboard(
                                        `${evalu.dimension} - Score: ${evalu.score} / 10\n${evalu.rationale}`
                                      )
                                    }
                                  >
                                    Copy Details
                                  </Button>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p>No evaluations available.</p>
                          )}
                        </div>
                      )}
                    </ScrollArea>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}