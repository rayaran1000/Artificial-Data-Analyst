import React, { useState, useEffect } from 'react';
import { Database, Upload, Link, Cloud, Edit, Download } from "lucide-react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface DataProps {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const DataControl: React.FC<DataProps> = ({ darkMode }) => {
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [apiLink, setApiLink] = useState('');
  const [cloudService, setCloudService] = useState('');
  const [awsDetails, setAwsDetails] = useState({
    accessKeyId: '',
    secretAccessKey: '',
    region: ''
  });
  const [gcpDetails, setGcpDetails] = useState({
    projectId: '',
    serviceAccountKey: ''
  });
  const [error, setError] = useState('');
  const [showAlert, setShowAlert] = useState(false);
  const [isEditable, setIsEditable] = useState(false);

  useEffect(() => {
    // Fetch user's saved data on component load
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch("http://localhost:8000/datacontrol/get", {
          method: "GET",
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setFileName(data.file);
          setApiLink(data.apiLink);
          setCloudService(data.cloudService);
          setAwsDetails(data.awsDetails || { accessKeyId: (data.awsaccesskeyID), secretAccessKey: (data.awsaccesskey), region: (data.awsregion) });
          setGcpDetails(data.gcpDetails || { projectId: (data.gcpprojectID), serviceAccountKey: (data.gcpaccountkey) });
        }
        else
          try {
            const token = localStorage.getItem('token');
            const response = await fetch("http://localhost:8000/datacontrol/create", {
              method: "POST",
              headers: {
                'Authorization': `Bearer ${token}`
              }
            });
            if (response.ok) {
              console.log("User dummy record created successfully")
            }
            } catch (error){
              console.error("Failed to create user dummy record:", error);
            }
    

      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    };

    fetchUserData();
  }, []);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
    }
  };

  const handleApiLinkChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setApiLink(event.target.value);
  };

  const handleAwsDetailsChange = (key: string, value: string) => {
    setAwsDetails(prevDetails => ({ ...prevDetails, [key]: value }));
  };

  const handleGcpDetailsChange = (key: string, value: string) => {
    setGcpDetails(prevDetails => ({ ...prevDetails, [key]: value }));
  };

  const handleEditDataSources = () => {
    setIsEditable(!isEditable);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    setShowAlert(false);
  
    const formData = new FormData();
  
    if (file) {
      formData.append("file", file);
    }
  
    formData.append("apiLink", apiLink);
    formData.append("cloudService", cloudService);
  
    if (cloudService === "AWS") {
      formData.append("aws_access_key_ID", awsDetails.accessKeyId);
      formData.append("aws_access_key", awsDetails.secretAccessKey);
      formData.append("aws_region", awsDetails.region);
    } else if (cloudService === "GCP") {
      formData.append("gcp_account_key", gcpDetails.serviceAccountKey);
      formData.append("gcp_project_ID", gcpDetails.projectId);
    }
  
    try {
      const token = localStorage.getItem('token');
      const response = await fetch("http://localhost:8000/datacontrol/update", {
        method: "PUT",
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });
  
      if (response.ok) {
        console.log("Data updated successfully");
        setIsEditable(false);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update data.');
      }
    } catch (error) {
      console.error("Error updating data:", error);
      setError('An unexpected error occurred.');
    }
  };

  const handleDownloadFile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch("http://localhost:8000/datacontrol/download", {
        method: "GET",
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
  
      if (response.ok) {
        // Get the filename from the Content-Disposition header if available
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'download.csv';
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
  
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else {
        const errorData = await response.json();
        setError(`Failed to download file: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("Error downloading file:", error);
      setError('An unexpected error occurred while trying to download the file.');
    }
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
            <Database className="mr-2 h-6 w-6" />
            <h1 className="text-3xl font-bold">Data Control</h1>
          </div>
          <div className="flex flex-col space-y-2">
            <Button variant="outline" onClick={handleEditDataSources}>
              <Edit className="mr-2 h-4 w-4" />
              {isEditable ? "Cancel Edit" : "Edit Data Sources"}
            </Button>
            <Button
              variant="outline"
              onClick={handleDownloadFile}
              disabled={!fileName}
            >
              <Download className="mr-2 h-4 w-4" />
              Download Data File
            </Button>
          </div>
        </motion.div>

        {showAlert && (
          <Alert variant="destructive" className="mb-6">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>
              At least one data source should be provided for analysis.
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Upload className="mr-2 h-5 w-5" />
                File Upload
              </CardTitle>
              <CardDescription>Upload or replace your data file here</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid w-full max-w-sm items-center gap-1.5">
                <Label htmlFor="file-upload">Choose file</Label>
                <Input
                  id="file-upload"
                  type="file"
                  onChange={handleFileChange}
                  className="cursor-pointer"
                  disabled={!isEditable}
                />
              </div>
              {(file || fileName) && (
                <div className="mt-2 flex items-center justify-between">
                  <p className="text-sm">
                    Selected file: {file ? file.name : fileName}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Link className="mr-2 h-5 w-5" />
                API Connection
              </CardTitle>
              <CardDescription>Enter your data pipeline API link</CardDescription>
            </CardHeader>
            <CardContent>
              <Input
                type="url"
                placeholder="https://api.example.com/data"
                value={apiLink}
                onChange={handleApiLinkChange}
                disabled={!isEditable}
              />
            </CardContent>
          </Card>

          <Card className="col-span-full">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Cloud className="mr-2 h-5 w-5" />
                Cloud Connection
              </CardTitle>
              <CardDescription>Provide your cloud service credentials</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs value={cloudService} onValueChange={setCloudService}>
                <TabsList>
                  <TabsTrigger value="AWS">AWS</TabsTrigger>
                  <TabsTrigger value="GCP">GCP</TabsTrigger>
                </TabsList>

                <TabsContent value="AWS">
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>Access Key ID</Label>
                        <Input
                          value={awsDetails.accessKeyId}
                          onChange={(e) => handleAwsDetailsChange('accessKeyId', e.target.value)}
                          disabled={!isEditable}
                        />
                      </div>
                      <div>
                        <Label>Secret Access Key</Label>
                        <Input
                          value={awsDetails.secretAccessKey}
                          onChange={(e) => handleAwsDetailsChange('secretAccessKey', e.target.value)}
                          disabled={!isEditable}
                        />
                      </div>
                    </div>
                    <Label>Region</Label>
                    <Input
                      value={awsDetails.region}
                      onChange={(e) => handleAwsDetailsChange('region', e.target.value)}
                      disabled={!isEditable}
                    />
                  </div>
                </TabsContent>

                <TabsContent value="GCP">
                  <div className="space-y-4">
                    <Label>Project ID</Label>
                    <Input
                      value={gcpDetails.projectId}
                      onChange={(e) => handleGcpDetailsChange('projectId', e.target.value)}
                      disabled={!isEditable}
                    />
                    <Label>Service Account Key</Label>
                    <Input
                      value={gcpDetails.serviceAccountKey}
                      onChange={(e) => handleGcpDetailsChange('serviceAccountKey', e.target.value)}
                      disabled={!isEditable}
                    />
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {isEditable && (
            <div className="col-span-full flex justify-end mt-4">
              <Button type="submit" variant="default">
                Save Changes
              </Button>
            </div>
          )}
        </form>
      </main>
    </div>
  );
};

export default DataControl;