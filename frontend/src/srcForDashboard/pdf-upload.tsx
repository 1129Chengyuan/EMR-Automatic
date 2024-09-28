import type { SetStateAction } from 'react'
import { useEffect, useState } from 'react'
// import { useRouter } from 'next/navigation'
import { Button } from "./components/ui/button"
import { Input } from "./components/ui/input"
import { Progress } from "./components/ui/progress"
import { ScrollArea } from "./components/ui/scroll-area"
import { Upload, FileText, Check, File, Search } from "lucide-react"
import { User } from "lucide-react"

const templates = [
  { id: 'chest-pain', name: 'Chest Pain' },
  { id: 'abdominal-pain', name: 'Abdominal Pain' },
  { id: 'headache', name: 'Headache' },
]

export default function PDFUploadWithTemplates() {
  // const router = useRouter()

  // useEffect(() => {
  //   if (!router) return;
  // }, [router]);

  const [file, setFile] = useState<File | null>(null)
  const [converting, setConverting] = useState(false)
  const [conversionProgress, setConversionProgress] = useState(0)
  const [converted, setConverted] = useState(false)
  const [selectedPreviousFile, setSelectedPreviousFile] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [currentPatient, setCurrentPatient] = useState<string | null>(null)
  const [pdfNamesForPatient, setPdfNamesForPatient] = useState<string[]>([])

  const patientNames = ["john doe", "bob junior", "mira amir", "hunlee li", "sanvi jain", "james bond"].sort()

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    setFile(files[0])
    if (files && files[0] && files[0].type === "application/pdf") {
      setFile(files[0])
      setSelectedPreviousFile(null)
    } else {
      alert("Please select a valid PDF file.")
    }
  }

  const handlePreviousFileSelect = (fileName: string) => {
    setSelectedPreviousFile(fileName)
    setFile(null)
    setConverted(false)
  }

  const handleUpload = async () => {
    if (!file && !selectedPreviousFile) return
  
    setConverting(true)
    setConversionProgress(0)
  
    try {
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      } else {
        formData.append('file', selectedPreviousFile);
      }
  
      const response = await fetch('http://localhost:5000/uploadpdf', {
        method: 'POST',
        body: formData,
      });
  
      const data = await response.json();
  
      if (response.ok) {
        if (data.message.includes('successful')) {
          window.location.href = '/dashboard';
        }
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setConverting(false)
      setConverted(true)
    }
  }
  const handleTemplateSelect = (templateId: string) => {
    window.location.href = `/patient-details?template=${templateId}`
  }

  const handlePatientChange = async (patientName: string) => {
    setCurrentPatient(patientName)

    // fetch files for the patient
    try {
      const response = await fetch(`http://localhost:5000/getpdfs?name=${patientName}`);
      const data = await response.json();
      setPdfNamesForPatient([]);
      if (response.ok) {
        setPdfNamesForPatient(data.pdfs);
      } else {
        console.error('Failed to fetch PDFs:', data.message);
      }
    } catch (error) {
      console.error('Error fetching PDFs:', error);
    }
  }

  const handleSearchChange = (event: { target: { value: SetStateAction<string> } }) => {
    setSearchQuery(event.target.value)
  }

  const filteredNames = patientNames.filter(patientN => 
    patientN.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const filteredFileNames = pdfNamesForPatient.filter(pdfName =>
    pdfName.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-64 bg-white p-6 shadow-md flex flex-col">
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <Input
              type="text"
              placeholder="Search patients..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="pl-8"
            />
          </div>
        </div>
        <h2 className="text-xl font-semibold mb-4">Patients</h2>
        <ScrollArea className="flex-grow">
          {filteredNames.map((patientName) => (
            <Button
              key={patientName}
              // variant="ghost"
              className={`w-full justify-start mb-2 ${selectedPreviousFile === patientName ? 'bg-primary/10' : ''}`}
              onClick={() => handlePatientChange(patientName)}
            >
              <User className="mr-2 h-4 w-4" />
              {patientName}
            </Button>
          ))}
        </ScrollArea>
      </div>

      {currentPatient && (<div className="w-64 bg-white p-6 shadow-md flex flex-col">
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <Input
              type="text"
              placeholder="Search patient's documents..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="pl-8"
            />
          </div>
        </div>
        <h2 className="text-xl font-semibold mb-4">{currentPatient}</h2>
        <ScrollArea className="flex-grow">
          {filteredFileNames.map((fileName) => (
            <Button
              key={fileName}
              // variant="ghost"
              className={`w-full justify-start mb-2 ${selectedPreviousFile === fileName ? 'bg-primary/10' : ''}`}
              onClick={() => handlePreviousFileSelect(fileName)}
            >
              <File className="mr-2 h-4 w-4" />
              {fileName}
            </Button>
          ))}
        </ScrollArea>
      </div>)}

      <div className="flex-1 p-6 overflow-auto">
        <h1 className="text-2xl font-bold mb-4">PDF Upload and Conversion</h1>
        
        {!converted && (
          <div className="space-y-4">
            <Input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
            />
            <Button onClick={handleUpload} disabled={(!file && !selectedPreviousFile) || converting}>
              {converting ? "Converting..." : `Upload and Convert ${selectedPreviousFile || ''}`}
              {!converting && <Upload className="ml-2 h-4 w-4" />}
            </Button>
          </div>
        )}

        {converting && (
          <div className="space-y-2">
            <Progress value={conversionProgress} className="w-full" />
            <p className="text-sm text-gray-500">Converting PDF to text...</p>
          </div>
        )}

        {converted && (
          <div className="space-y-4">
            <div className="flex items-center space-x-2 text-green-600">
              <FileText className="h-5 w-5" />
              <span>PDF converted successfully!</span>
              <Check className="h-5 w-5" />
            </div>
            
            <div className="space-y-2">
              <h2 className="text-lg font-semibold">Select a differential diagnosis template:</h2>
              <div className="flex flex-wrap gap-2">
                {templates.map((template) => (
                  <Button
                    key={template.id}
                    onClick={() => handleTemplateSelect(template.id)}
                  >
                    {template.name}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}