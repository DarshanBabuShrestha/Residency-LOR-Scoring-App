import React, { useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

export default function Home() {
  const [file, setFile] = useState(null);
  const [lorText, setLorText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setLorText('');
  };

  const handleTextChange = (e) => {
    setLorText(e.target.value);
    setFile(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    } else if (lorText.trim()) {
      formData.append('lor_text', lorText);
    } else {
      setError('Please provide a file or text.');
      setLoading(false);
      return;
    }
    try {
      const res = await axios.post('http://localhost:8000/score-lor', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Error scoring LOR.');
    }
    setLoading(false);
  };

  const domainScores = result
    ? [
        { domain: 'Patient Care', score: result.patient_care },
        { domain: 'Medical Knowledge', score: result.medical_knowledge },
        { domain: 'Interpersonal', score: result.interpersonal },
        { domain: 'Professionalism', score: result.professionalism },
        { domain: 'Scholarly', score: result.scholarly },
        { domain: 'Author Credibility', score: result.author_credibility },
      ]
    : [];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-4">
      <h1 className="text-3xl font-bold mb-4">Residency LOR Scoring App</h1>
      <form
        className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 w-full max-w-lg"
        onSubmit={handleSubmit}
      >
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Upload LOR (PDF/DOCX):</label>
          <input type="file" accept=".pdf,.docx" onChange={handleFileChange} className="mb-2" />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Or paste LOR text:</label>
          <textarea
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            rows={6}
            value={lorText}
            onChange={handleTextChange}
            placeholder="Paste LOR text here..."
          />
        </div>
        <button
          type="submit"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          disabled={loading}
        >
          {loading ? 'Scoring...' : 'Score LOR'}
        </button>
        {error && <p className="text-red-500 mt-2">{error}</p>}
      </form>
      {result && (
        <div className="w-full max-w-2xl bg-white rounded shadow p-6">
          <h2 className="text-xl font-semibold mb-2">Results</h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <ul>
                <li>Patient Care: <b>{result.patient_care}</b></li>
                <li>Medical Knowledge: <b>{result.medical_knowledge}</b></li>
                <li>Interpersonal: <b>{result.interpersonal}</b></li>
                <li>Professionalism: <b>{result.professionalism}</b></li>
                <li>Scholarly: <b>{result.scholarly}</b></li>
                <li>Author Credibility: <b>{result.author_credibility}</b></li>
                <li className="text-red-600">Deductions: <b>{result.deductions}</b></li>
                <li className="text-green-700">Final Score: <b>{result.final_score}</b></li>
              </ul>
            </div>
            <div>
              <ResponsiveContainer width="100%" height={220}>
                <RadarChart data={domainScores} outerRadius={80}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="domain" />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                  <Radar name="Score" dataKey="score" stroke="#2563eb" fill="#60a5fa" fillOpacity={0.6} />
                </RadarChart>
              </ResponsiveContainer>
              <ResponsiveContainer width="100%" height={120}>
                <BarChart data={domainScores}>
                  <XAxis dataKey="domain" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="score" fill="#2563eb" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
