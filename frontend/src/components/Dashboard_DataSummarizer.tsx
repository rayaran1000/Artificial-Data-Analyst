import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Settings, RefreshCw } from "lucide-react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface DataSummarizerProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

type SummarizationMethod = 'default' | 'llm-enriched' | 'column-names-only';

const DataSummarizer: React.FC<DataSummarizerProps> = ({ darkMode }) => {
  const [summarizationMethod, setSummarizationMethod] = useState<SummarizationMethod>('default');
  const [temperature, setTemperature] = useState<number>(0.7);
  const [summary, setSummary] = useState<any>(null);  // Update type to `any` for structured data
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  const fetchSummary = async () => {
    try {
      setError('')
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/datasummarizer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ selected_method: summarizationMethod, temperature })
      });

      if (response.ok) {
        const data = await response.json();
        setSummary(data.summary);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch summary.');
      }
    } catch (error) {
      console.error("Error fetching summary:", error);
      setError('An unexpected error occurred while fetching the summary.');
    }
  };

  const handleMethodChange = (value: string) => {
    setSummarizationMethod(value as SummarizationMethod);
  };

  const handleTemperatureChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setTemperature(parseFloat(event.target.value));
  };

  const navigateToDataControl = () => {
    navigate('/datacontrol');
  };

  const handleGenerateSummary = () => {
    fetchSummary();
  };

  const renderTable = () => {
    if (!summary) return null;

    if (summarizationMethod === 'default' && summary.fields) {
      return (
        <table className="min-w-full bg-white dark:bg-gray-800">
          <thead>
            <tr>
              <th className="px-4 py-2">Field Name</th>
              <th className="px-4 py-2">Data Type</th>
              <th className="px-4 py-2">Sample Values</th>
            </tr>
          </thead>
          <tbody>
            {summary.fields.map((field: any, index: number) => (
              <tr key={index} className="text-center">
                <td className="border px-4 py-2">{field.column}</td>
                <td className="border px-4 py-2">{field.properties.dtype}</td>
                <td className="border px-4 py-2">{field.properties.samples.join(', ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      );
    } else if (summarizationMethod === 'llm-enriched' && summary.fields) {
      return (
        <>
          <div className="mb-4">
            <h2 className="text-xl font-bold">Dataset Name</h2>
            <p>{summary.dataset_name || 'N/A'}</p>
          </div>
          <div className="mb-4">
            <h2 className="text-xl font-bold">Dataset Description</h2>
            <p>{summary.dataset_description || 'N/A'}</p>
          </div>
          <table className="min-w-full bg-white dark:bg-gray-800">
            <thead>
              <tr>
                <th className="px-4 py-2">Field Name</th>
                <th className="px-4 py-2">Field Description</th>
                <th className="px-4 py-2">Semantic Type</th>
              </tr>
            </thead>
            <tbody>
              {summary.fields.map((field: any, index: number) => (
                <tr key={index} className="text-center">
                  <td className="border px-4 py-2">{field.column}</td>
                  <td className="border px-4 py-2">{field.field_description || 'N/A'}</td>
                  <td className="border px-4 py-2">{field.semantic_type || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      );
    } else if (summarizationMethod === 'column-names-only' && summary.field_names) {
      return (
        <>
          <h2 className="text-xl font-bold mb-4">Columns</h2>
          <ul>
            {summary.field_names.map((name: string, index: number) => (
              <li key={index} className="border px-4 py-2">{name}</li>
            ))}
          </ul>
        </>
      );
    }
    return <p>No data available for the selected method.</p>;
  };

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-900'}`}>
      <main className="flex-grow container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center justify-between mb-8"
        >
          <div className="flex items-center">
            <FileText className="mr-2 h-6 w-6" />
            <h1 className="text-3xl font-bold">Data Summarizer</h1>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" onClick={navigateToDataControl}>
              <Settings className="mr-2 h-4 w-4" />
              Manage/Modify Data Source
            </Button>
          </div>
        </motion.div>
        
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Data Summary</span>
              <div className="flex flex-col items-start space-y-2">
                <div className="flex space-x-2">
                  <Select value={summarizationMethod} onValueChange={handleMethodChange}>
                    <SelectTrigger className="w-[200px]">
                      <SelectValue placeholder="Select method" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="default">Default</SelectItem>
                      <SelectItem value="llm-enriched">LLM Enriched</SelectItem>
                      <SelectItem value="column-names-only">Column Names Only</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="outline" onClick={handleGenerateSummary}>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Generate Data Summary
                  </Button>
                </div>
                <div className="flex items-center space-x-4 mt-2">
                  <label htmlFor="temperature-slider" className="text-sm font-medium">
                    Temperature
                  </label>
                  <input
                    id="temperature-slider"
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={temperature}
                    onChange={handleTemperatureChange}
                    className="w-full"
                  />
                  <span className="text-sm">{temperature.toFixed(1)}</span>
                </div>
              </div>
            </CardTitle>
            <CardDescription>
              Summary of your data based on the selected method
            </CardDescription>
          </CardHeader>
          <CardContent>{renderTable()}</CardContent>
        </Card>
      </main>
    </div>
  );
};

export default DataSummarizer;
