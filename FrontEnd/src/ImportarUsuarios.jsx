import React, { useState } from 'react';
import { Button, Typography, Paper, Box, CircularProgress } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';

function ImportarUsuarios() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const apiUrl = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://rock-symphony-91f7e39d835d.herokuapp.com';

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;

    setFile(selectedFile);

    if (selectedFile.name.endsWith('.csv')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target.result;
        const lines = text.split('\n').slice(0, 5);
        setPreview(lines.join('\n'));
      };
      reader.readAsText(selectedFile);
    } else {
      setPreview(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Selecione um arquivo primeiro!');
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        alert("Usuário não autenticado. Por favor, faça login.");
        setLoading(false);
        return;
      }

      const response = await fetch(`${apiUrl}/api/importar-usuarios`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        alert('Arquivo enviado com sucesso!');
        setFile(null);
        setPreview(null);
      } else {
        alert('Erro ao enviar o arquivo.');
      }
    } catch (error) {
      console.error('Erro ao enviar arquivo:', error);
      alert('Erro na comunicação com o servidor.');
    }

    setLoading(false);
  };

  return (
    <Paper elevation={3} sx={{ p: 3, textAlign: 'center', maxWidth: 500, mx: 'auto', mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        Importar Usuários
      </Typography>

      <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
        <Button
          variant="contained"
          component="label"
          startIcon={<UploadFileIcon />}
          sx={{ backgroundColor: '#1976d2', '&:hover': { backgroundColor: '#125ea8' } }}
        >
          Escolher Arquivo
          <input type="file" accept=".csv,.docx" hidden onChange={handleFileChange} />
        </Button>

        {file && <Typography variant="body1" color="textSecondary">{file.name}</Typography>}

        {preview && (
          <Paper variant="outlined" sx={{ p: 2, maxHeight: 150, overflow: 'auto', bgcolor: '#f9f9f9' }}>
            <Typography variant="subtitle2">Pré-visualização (CSV):</Typography>
            <pre style={{ fontSize: '0.85rem', whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>{preview}</pre>
          </Paper>
        )}

        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={loading}
          sx={{ mt: 2, width: '100%' }}
        >
          {loading ? <CircularProgress size={24} /> : 'Enviar Arquivo'}
        </Button>
      </Box>
    </Paper>
  );
}

export default ImportarUsuarios;
