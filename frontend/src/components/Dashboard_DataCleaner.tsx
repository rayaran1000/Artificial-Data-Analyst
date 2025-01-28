import { useState, useEffect } from 'react';
import { ArrowLeft, Wand2, Filter, Download } from 'lucide-react';
import { motion } from "framer-motion";
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface DataCleanerPageProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

interface DataFrameInfo {
  topRows: any[];
  rowCount: number;
  columnCount: number;
  columnTypes: { [key: string]: string };
  featureTypes: { [key: string]: any };
}

export default function DataCleaner({ darkMode, }: DataCleanerPageProps) {
  const navigate = useNavigate();
  const [dataFrameInfo, setDataFrameInfo] = useState<DataFrameInfo | null>(null);
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedColumnsForEngineering, setSelectedColumnsForEngineering] = useState<string[]>([]);
  const [selectedColumnsForSelection, setSelectedColumnsForSelection] = useState<string[]>([]);
  const [showColumnSelection, setShowColumnSelection] = useState<'engineering' | 'selection' | null>(null);
  const [selectedFeatureTask, setSelectedFeatureTask] = useState<string | null>(null);
  const [selectedFeatureSubTask, setSelectedFeatureSubTask] = useState<string | null>(null);
  const [selectedTargetFeature, setSelectedTargetFeature] = useState<string | null>(null);

  const featureEngineeringSubTasks: { [key: string]: string[] } = {
    'Missing Data Imputation': [
      'MeanImputer',
      'MedianImputer',
      'RandomSampleImputer',
      'EndTailImputer',
      'AddMissingIndicator',
      'DropMissingData'
    ],
    'Categorical Encoding': [
      'OneHotEncoder',
      'OrdinalEncoder',
      'CountEncoder',
      'FrequencyEncoder',
      'MeanEncoder'
    ],
    'Discretisation': [
      'EqualFrequencyDiscretiser',
      'EqualWidthDiscretiser',
      'GeometricWidthDiscretiser',
      'DecisionTreeDiscretiser'
    ],
    'Outlier Capping or Removal': [
      'GaussianOutlierCapper',
      'IQROutlierCapper'
    ],
    'Feature Transformation': [
      'LogTransformer',
      'LogCpTransformer',
      'ReciprocalTransformer',
      'SquareRootTransformer',
      'BoxCoxTransformer',
      'YeoJohnsonTransformer'
    ],
    'Feature Scaling': ['MeanNormalizationScaler'],
    'Datetime Feature Handling': ['DatetimeFeatures']
  };

  const featureSelectionSubTasks = [
    'DropFeatures',
    'DropConstantFeatures',
    'DropDuplicateFeatures',
    'DropCorrelatedFeatures',
    'SmartCorrelationSelection',
    'ShuffleFeaturesSelector',
    'SelectBySingleFeaturePerformance',
    'RecursiveFeatureElimination'
  ];

  useEffect(() => {
    fetchDataFrameInfo();
  }, []);

  const fetchDataFrameInfo = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/datacleaner/dataframe-info', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!response.ok) throw new Error('Failed to fetch dataframe info');
      const data = await response.json();
      setDataFrameInfo(data);
    } catch (error) {
      console.error('Error fetching dataframe info:', error);
      alert('Failed to fetch dataframe info. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleColumnSelectionSubmit = async (type: 'engineering' | 'selection') => {
    try {
      const columns = type === 'engineering' ? selectedColumnsForEngineering : selectedColumnsForSelection;
      const featureTask = selectedFeatureTask;
      const featureSubTask = selectedFeatureSubTask;
      const targetFeature = selectedTargetFeature;

      const response = await fetch(`http://localhost:8000/datacleaner/${type}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ columns, featureTask, featureSubTask, targetFeature })
      });

      if (!response.ok) throw new Error(`Failed to submit columns for ${type}`);
      const data = await response.json();
      setDataFrameInfo(data);

      // Close column selection and show the respective section
      setShowColumnSelection(null);
      setActiveSection(type);
    } catch (error) {
      console.error(`Error submitting columns for ${type}:`, error);
      alert(`Failed to submit columns for ${type}. Please try again.`);
    }
  };

  const handleDownloadData = async () => {
    try {
      const response = await fetch('http://localhost:8000/datacleaner/download', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to download data');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'edited_data.csv';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading data:', error);
      alert('Failed to download data. Please try again.');
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
            <Button variant="ghost" onClick={() => {
              navigate(-1);
              fetchDataFrameInfo();
            }} className="mr-4">
              <ArrowLeft className="h-6 w-6" />
            </Button>
            <h1 className="text-3xl font-bold">Data Cleaner</h1>
          </div>
        </motion.div>

        <div className="grid grid-cols-12 gap-6">
          {/* Data Display Section */}
          <div className="col-span-8 space-y-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-semibold">Data Preview</h2>
                  <div className="flex gap-2">
                    <Button 
                      variant="outline"
                      onClick={handleDownloadData}
                      disabled={isLoading}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download Data
                    </Button>
                    <Button onClick={fetchDataFrameInfo} disabled={isLoading}>
                      {isLoading ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      ) : (
                        "Back to Original Data"
                      )}
                    </Button>
                  </div>
                </div>
                {isLoading ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                  </div>
                ) : dataFrameInfo ? (
                  <ScrollArea className="h-64">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          {dataFrameInfo.topRows[0] && Object.keys(dataFrameInfo.topRows[0]).map((key) => (
                            <TableHead key={key}>{key}</TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {dataFrameInfo.topRows.map((row, index) => (
                          <TableRow key={index}>
                            {Object.values(row).map((value: any, cellIndex) => (
                              <TableCell key={cellIndex}>{value}</TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </ScrollArea>
                ) : (
                  <p>No data available</p>
                )}
                {dataFrameInfo && (
                  <div className="mt-4">
                    <p>Number of rows: {dataFrameInfo.rowCount}</p>
                    <p>Number of columns: {dataFrameInfo.columnCount}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <h2 className="text-xl font-semibold mb-4">Column Information</h2>
                {dataFrameInfo && (
                  <ScrollArea className="h-48">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Column Name</TableHead>
                          <TableHead>Data Type</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {Object.entries(dataFrameInfo.columnTypes).map(([column, type], index) => (
                          <TableRow key={index}>
                            <TableCell>{column}</TableCell>
                            <TableCell>{type}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </ScrollArea>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Feature Engineering and Selection Section - moved to the right */}
          <div className="col-span-4 space-y-4">
            {/* Column Selection Modal */}
            {showColumnSelection && (
              <Card className="mt-2">
                <CardContent className="p-4">
                  <h3 className="text-lg font-semibold mb-4">
                    Select columns for {showColumnSelection === 'engineering' ? 'Feature Engineering' : 'Feature Selection'}
                  </h3>
                  
                  {/* Dropdown for Choosing Independent Features */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" className="w-full justify-between">
                        Choose Independent Features
                        <span className="ml-2">
                          ({(showColumnSelection === 'engineering' ? 
                            selectedColumnsForEngineering : 
                            selectedColumnsForSelection).length} selected)
                        </span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56">
                      {dataFrameInfo && Object.keys(dataFrameInfo.columnTypes).map(column => (
                        <DropdownMenuItem
                          key={column}
                          onClick={() => {
                            const setColumns = showColumnSelection === 'engineering' ? 
                              setSelectedColumnsForEngineering : 
                              setSelectedColumnsForSelection;
                            const currentColumns = showColumnSelection === 'engineering' ? 
                              selectedColumnsForEngineering : 
                              selectedColumnsForSelection;
                            
                            setColumns(
                              currentColumns.includes(column) ?
                                currentColumns.filter(c => c !== column) :
                                [...currentColumns, column]
                            );
                          }}
                        >
                          <Checkbox
                            checked={(showColumnSelection === 'engineering' ? 
                              selectedColumnsForEngineering : 
                              selectedColumnsForSelection).includes(column)}
                            className="mr-2"
                          />
                          {column}
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>

                  {/* Dropdown for Choosing Target Feature */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" className="w-full justify-between mt-4">
                        {selectedTargetFeature || "Choose Target Feature"}
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56">
                      {dataFrameInfo && Object.keys(dataFrameInfo.columnTypes).map(column => (
                        <DropdownMenuItem
                          key={column}
                          onClick={() => setSelectedTargetFeature(column)}
                        >
                          {column}
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>

                  <div className="mt-4">
                    <h4 className="text-sm font-medium mb-2">Selected Independent Columns:</h4>
                    <div className="flex flex-wrap gap-2">
                      {(showColumnSelection === 'engineering' ? 
                        selectedColumnsForEngineering : 
                        selectedColumnsForSelection).map(column => (
                        <div 
                          key={column}
                          className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-100 
                             px-2 py-1 rounded-md text-sm flex items-center gap-1"
                        >
                          {column}
                          <button
                            onClick={() => {
                              const setColumns = showColumnSelection === 'engineering' ? 
                                setSelectedColumnsForEngineering : 
                                setSelectedColumnsForSelection;
                              const currentColumns = showColumnSelection === 'engineering' ? 
                                selectedColumnsForEngineering : 
                                selectedColumnsForSelection;
                              
                              setColumns(currentColumns.filter(c => c !== column));
                            }}
                            className="ml-1 hover:text-red-500"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                      {(showColumnSelection === 'engineering' ? 
                        selectedColumnsForEngineering : 
                        selectedColumnsForSelection).length === 0 && (
                        <span className="text-gray-500 text-sm">No columns selected</span>
                      )}
                    </div>
                  </div>

                  {/* Feature Engineering Task Selection */}
                  {showColumnSelection === 'engineering' && (
                    <>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="outline" className="w-full justify-between mt-4">
                            {selectedFeatureTask || "Select Feature Engineering Task"}
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent className="w-56">
                          {Object.keys(featureEngineeringSubTasks).map(task => (
                            <DropdownMenuItem
                              key={task}
                              onClick={() => {
                                setSelectedFeatureTask(task);
                                setSelectedFeatureSubTask(null); // Reset sub-task when main task changes
                              }}
                            >
                              {task}
                            </DropdownMenuItem>
                          ))}
                        </DropdownMenuContent>
                      </DropdownMenu>

                      {selectedFeatureTask && (
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="outline" className="w-full justify-between mt-4">
                              {selectedFeatureSubTask || "Select Specific Method"}
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent className="w-56">
                            {featureEngineeringSubTasks[selectedFeatureTask]?.map(subTask => (
                              <DropdownMenuItem
                                key={subTask}
                                onClick={() => setSelectedFeatureSubTask(subTask)}
                              >
                                {subTask}
                              </DropdownMenuItem>
                            ))}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      )}

                      {selectedColumnsForEngineering.length > 0 && selectedFeatureTask && selectedFeatureSubTask && (
                        <div className="flex justify-end space-x-2 mt-4">
                          <Button 
                            variant="outline" 
                            onClick={() => {
                              setShowColumnSelection(null);
                              setSelectedFeatureTask(null);
                              setSelectedFeatureSubTask(null);
                            }}
                          >
                            Cancel
                          </Button>
                          <Button 
                            onClick={() => {
                              handleColumnSelectionSubmit('engineering');
                              setSelectedFeatureTask(null);
                              setSelectedFeatureSubTask(null);
                            }}
                          >
                            Proceed with Engineering
                          </Button>
                        </div>
                      )}
                    </>
                  )}

                  {/* Feature Selection Task Selection */}
                  {showColumnSelection === 'selection' && (
                    <>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="outline" className="w-full justify-between mt-4">
                            {selectedFeatureSubTask || "Select Feature Selection Method"}
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent className="w-56">
                          {featureSelectionSubTasks.map(subTask => (
                            <DropdownMenuItem
                              key={subTask}
                              onClick={() => setSelectedFeatureSubTask(subTask)}
                            >
                              {subTask}
                            </DropdownMenuItem>
                          ))}
                        </DropdownMenuContent>
                      </DropdownMenu>

                      {selectedColumnsForSelection.length > 0 && selectedFeatureSubTask && (
                        <div className="flex justify-end space-x-2 mt-4">
                          <Button 
                            variant="outline" 
                            onClick={() => {
                              setShowColumnSelection(null);
                              setSelectedFeatureSubTask(null);
                            }}
                          >
                            Cancel
                          </Button>
                          <Button 
                            onClick={() => {
                              handleColumnSelectionSubmit('selection');
                              setSelectedFeatureSubTask(null);
                            }}
                          >
                            Proceed with Selection
                          </Button>
                        </div>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Feature Engineering Button */}
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => {
                if (activeSection === 'engineering') {
                  setActiveSection(null);
                } else {
                  setShowColumnSelection('engineering');
                }
              }}
            >
              <Wand2 className="mr-2 h-4 w-4" />
              Feature Engineering
            </Button>

            {/* Feature Selection Button */}
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => {
                if (activeSection === 'selection') {
                  setActiveSection(null);
                } else {
                  setShowColumnSelection('selection');
                }
              }}
            >
              <Filter className="mr-2 h-4 w-4" />
              Feature Selection
            </Button>

            {/* Rest of your existing feature engineering and selection sections... */}
          </div>
        </div>
      </main>
    </div>
  );
}