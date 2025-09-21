import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Alert,
  FormControlLabel,
  Switch,
  Stepper,
  Step,
  StepLabel,
  Chip,
  Divider,
  Grid,
  Paper,
  IconButton,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  Mic,
  CheckCircle,
  Error,
  Analytics,
  VideoFile,
  AudioFile,
  PictureAsPdf,
  Slideshow,
  Delete,
  PlayArrow,
  Pause,
} from '@mui/icons-material';
import { apiHelpers } from '../services/api';

const Upload = () => {
  const navigate = useNavigate();
  const [uploadState, setUploadState] = useState({
    pitchDeckFiles: [],
    audioFiles: [],
    videoFiles: [],
    uploading: false,
    progress: 0,
    error: null,
    success: false,
    result: null,
  });

  const [activeStep, setActiveStep] = useState(0);
  const [audioPlaying, setAudioPlaying] = useState({});

  const steps = [
    'Upload Materials',
    'Review Files',
    'Processing',
    'Results'
  ];

  // Dropzone for pitch deck (PDF/PPT)
  const onDropPitchDeck = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      setUploadState(prev => ({
        ...prev,
        error: 'Please upload only PDF or PPTX files'
      }));
      return;
    }

    setUploadState(prev => ({
      ...prev,
      pitchDeckFiles: [...prev.pitchDeckFiles, ...acceptedFiles],
      error: null
    }));
  }, []);

  // Dropzone for audio files
  const onDropAudio = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      setUploadState(prev => ({
        ...prev,
        error: 'Please upload only audio files (MP3, WAV, M4A, AAC)'
      }));
      return;
    }

    setUploadState(prev => ({
      ...prev,
      audioFiles: [...prev.audioFiles, ...acceptedFiles],
      error: null
    }));
  }, []);

  // Dropzone for video files
  const onDropVideo = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      setUploadState(prev => ({
        ...prev,
        error: 'Please upload only video files (MP4, MOV, AVI, WEBM)'
      }));
      return;
    }

    setUploadState(prev => ({
      ...prev,
      videoFiles: [...prev.videoFiles, ...acceptedFiles],
      error: null
    }));
  }, []);

  const pitchDeckDropzone = useDropzone({
    onDrop: onDropPitchDeck,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.ms-powerpoint': ['.ppt']
    },
    maxFiles: 5,
    disabled: uploadState.uploading
  });

  const audioDropzone = useDropzone({
    onDrop: onDropAudio,
    accept: {
      'audio/*': ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
    },
    maxFiles: 10,
    disabled: uploadState.uploading
  });

  const videoDropzone = useDropzone({
    onDrop: onDropVideo,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.webm', '.mkv', '.wmv']
    },
    maxFiles: 5,
    disabled: uploadState.uploading
  });

  // Helper functions
  const removeFile = (fileType, index) => {
    setUploadState(prev => ({
      ...prev,
      [fileType]: prev[fileType].filter((_, i) => i !== index)
    }));
  };

  const getFileIcon = (file) => {
    const extension = file.name.split('.').pop().toLowerCase();
    if (['pdf'].includes(extension)) return <PictureAsPdf />;
    if (['ppt', 'pptx'].includes(extension)) return <Slideshow />;
    if (['mp3', 'wav', 'm4a', 'aac', 'ogg', 'flac'].includes(extension)) return <AudioFile />;
    if (['mp4', 'mov', 'avi', 'webm', 'mkv', 'wmv'].includes(extension)) return <VideoFile />;
    return <Description />;
  };

  const getTotalFiles = () => {
    return uploadState.pitchDeckFiles.length + uploadState.audioFiles.length + uploadState.videoFiles.length;
  };

  const handleUpload = async () => {
    const totalFiles = getTotalFiles();
    if (totalFiles === 0) {
      setUploadState(prev => ({
        ...prev,
        error: 'Please upload at least one file (pitch deck, audio, or video)'
      }));
      return;
    }

    setUploadState(prev => ({
      ...prev,
      uploading: true,
      progress: 0,
      error: null
    }));

    setActiveStep(2); // Processing step

    try {
      const formData = new FormData();
      
      // Add pitch deck files
      uploadState.pitchDeckFiles.forEach((file, index) => {
        formData.append(`pitch_deck_${index}`, file);
      });
      
      // Add audio files
      uploadState.audioFiles.forEach((file, index) => {
        formData.append(`audio_${index}`, file);
      });
      
      // Add video files
      uploadState.videoFiles.forEach((file, index) => {
        formData.append(`video_${index}`, file);
      });

      // Add metadata
      formData.append('file_counts', JSON.stringify({
        pitch_deck: uploadState.pitchDeckFiles.length,
        audio: uploadState.audioFiles.length,
        video: uploadState.videoFiles.length
      }));

      const response = await apiHelpers.uploadWithProgress(
        formData,
        (progress) => {
          setUploadState(prev => ({
            ...prev,
            progress
          }));
        }
      );

      setUploadState(prev => ({
        ...prev,
        uploading: false,
        success: true,
        result: response.data.data
      }));

      setActiveStep(3); // Results step

    } catch (error) {
      const errorInfo = apiHelpers.handleError(error);
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        error: errorInfo.message
      }));
      setActiveStep(0); // Back to upload step
    }
  };

  const handleViewResults = () => {
    if (uploadState.result?.startup_id) {
      navigate(`/startup/${uploadState.result.startup_id}`);
    }
  };

  const handleReset = () => {
    setUploadState({
      pitchDeckFiles: [],
      audioFiles: [],
      videoFiles: [],
      uploading: false,
      progress: 0,
      error: null,
      success: false,
      result: null,
    });
    setActiveStep(0);
    setAudioPlaying({});
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Upload Startup Materials
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Upload your pitch decks, audio pitches, and video presentations for comprehensive AI-powered analysis
        </Typography>
      </Box>

      {/* Progress Stepper */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Stepper activeStep={activeStep} alternativeLabel>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {uploadState.error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setUploadState(prev => ({ ...prev, error: null }))}>
          {uploadState.error}
        </Alert>
      )}

      {/* Success Results */}
      {uploadState.success && uploadState.result && (
        <Card sx={{ mb: 4, border: '2px solid', borderColor: 'success.main' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <CheckCircle sx={{ color: 'success.main', mr: 2 }} />
              <Typography variant="h6" color="success.main">
                Upload Successful!
              </Typography>
            </Box>
            
            <Typography variant="body1" gutterBottom>
              Your startup evaluation has been completed successfully.
            </Typography>

            <Box sx={{ mt: 3, mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Processing Summary:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label="Data Extraction"
                  color={uploadState.result.processing_summary?.extraction_success ? 'success' : 'error'}
                  size="small"
                  icon={uploadState.result.processing_summary?.extraction_success ? <CheckCircle /> : <Error />}
                />
                <Chip
                  label="Public Data"
                  color={uploadState.result.processing_summary?.public_data_success ? 'success' : 'error'}
                  size="small"
                  icon={uploadState.result.processing_summary?.public_data_success ? <CheckCircle /> : <Error />}
                />
                <Chip
                  label="Risk Analysis"
                  color={uploadState.result.processing_summary?.risk_analysis_success ? 'success' : 'error'}
                  size="small"
                  icon={uploadState.result.processing_summary?.risk_analysis_success ? <CheckCircle /> : <Error />}
                />
                <Chip
                  label="Final Evaluation"
                  color={uploadState.result.processing_summary?.final_evaluation_success ? 'success' : 'error'}
                  size="small"
                  icon={uploadState.result.processing_summary?.final_evaluation_success ? <CheckCircle /> : <Error />}
                />
                <Chip
                  label="Investment Memo"
                  color={uploadState.result.processing_summary?.memo_generated ? 'success' : 'error'}
                  size="small"
                  icon={uploadState.result.processing_summary?.memo_generated ? <CheckCircle /> : <Error />}
                />
                <Chip
                  label="Meeting Scheduled"
                  color={uploadState.result.processing_summary?.meeting_scheduled ? 'success' : 'warning'}
                  size="small"
                  icon={uploadState.result.processing_summary?.meeting_scheduled ? <CheckCircle /> : <Error />}
                />
              </Box>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
              <Button
                variant="contained"
                startIcon={<Analytics />}
                onClick={handleViewResults}
                size="large"
              >
                View Analysis Results
              </Button>
              <Button
                variant="outlined"
                onClick={handleReset}
              >
                Upload Another
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Upload Forms */}
      {!uploadState.success && (
        <>
          <Grid container spacing={3}>
            {/* Pitch Deck Upload */}
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Slideshow color="primary" />
                    Pitch Decks
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Upload PDF or PowerPoint presentations
                  </Typography>

                  <Box
                    {...pitchDeckDropzone.getRootProps()}
                    sx={{
                      border: '2px dashed',
                      borderColor: pitchDeckDropzone.isDragActive ? 'primary.main' : 'grey.300',
                      borderRadius: 2,
                      p: 3,
                      textAlign: 'center',
                      cursor: uploadState.uploading ? 'not-allowed' : 'pointer',
                      backgroundColor: pitchDeckDropzone.isDragActive ? 'action.hover' : 'background.paper',
                      transition: 'all 0.2s ease',
                      minHeight: 120,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      '&:hover': {
                        borderColor: 'primary.main',
                        backgroundColor: 'action.hover',
                      }
                    }}
                  >
                    <input {...pitchDeckDropzone.getInputProps()} />
                    <CloudUpload sx={{ fontSize: 32, color: 'text.secondary', mb: 1 }} />
                    <Typography variant="body2" gutterBottom>
                      {pitchDeckDropzone.isDragActive ? 'Drop files here' : 'Drag & drop or click'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      PDF, PPT, PPTX (Max 5 files)
                    </Typography>
                  </Box>

                  {/* Pitch Deck Files List */}
                  {uploadState.pitchDeckFiles.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Uploaded Files ({uploadState.pitchDeckFiles.length})
                      </Typography>
                      {uploadState.pitchDeckFiles.map((file, index) => (
                        <Paper key={index} sx={{ p: 1, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getFileIcon(file)}
                          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                            <Typography variant="body2" noWrap>{file.name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {formatFileSize(file.size)}
                            </Typography>
                          </Box>
                          <IconButton
                            size="small"
                            onClick={() => removeFile('pitchDeckFiles', index)}
                            disabled={uploadState.uploading}
                          >
                            <Delete />
                          </IconButton>
                        </Paper>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Audio Upload */}
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AudioFile color="secondary" />
                    Audio Files
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Upload founder's audio pitch or presentation
                  </Typography>

                  <Box
                    {...audioDropzone.getRootProps()}
                    sx={{
                      border: '2px dashed',
                      borderColor: audioDropzone.isDragActive ? 'secondary.main' : 'grey.300',
                      borderRadius: 2,
                      p: 3,
                      textAlign: 'center',
                      cursor: uploadState.uploading ? 'not-allowed' : 'pointer',
                      backgroundColor: audioDropzone.isDragActive ? 'action.hover' : 'background.paper',
                      transition: 'all 0.2s ease',
                      minHeight: 120,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      '&:hover': {
                        borderColor: 'secondary.main',
                        backgroundColor: 'action.hover',
                      }
                    }}
                  >
                    <input {...audioDropzone.getInputProps()} />
                    <Mic sx={{ fontSize: 32, color: 'text.secondary', mb: 1 }} />
                    <Typography variant="body2" gutterBottom>
                      {audioDropzone.isDragActive ? 'Drop audio pitch here' : 'Drag & drop or click'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      MP3, WAV, M4A, AAC (Max 10 files)
                    </Typography>
                  </Box>

                  {/* Audio Files List */}
                  {uploadState.audioFiles.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Uploaded Files ({uploadState.audioFiles.length})
                      </Typography>
                      {uploadState.audioFiles.map((file, index) => (
                        <Paper key={index} sx={{ p: 1, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getFileIcon(file)}
                          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                            <Typography variant="body2" noWrap>{file.name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {formatFileSize(file.size)}
                            </Typography>
                          </Box>
                          <IconButton
                            size="small"
                            onClick={() => removeFile('audioFiles', index)}
                            disabled={uploadState.uploading}
                          >
                            <Delete />
                          </IconButton>
                        </Paper>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Video Upload */}
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <VideoFile color="success" />
                    Video Files
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Upload video presentations or demos
                  </Typography>

                  <Box
                    {...videoDropzone.getRootProps()}
                    sx={{
                      border: '2px dashed',
                      borderColor: videoDropzone.isDragActive ? 'success.main' : 'grey.300',
                      borderRadius: 2,
                      p: 3,
                      textAlign: 'center',
                      cursor: uploadState.uploading ? 'not-allowed' : 'pointer',
                      backgroundColor: videoDropzone.isDragActive ? 'action.hover' : 'background.paper',
                      transition: 'all 0.2s ease',
                      minHeight: 120,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center',
                      '&:hover': {
                        borderColor: 'success.main',
                        backgroundColor: 'action.hover',
                      }
                    }}
                  >
                    <input {...videoDropzone.getInputProps()} />
                    <VideoFile sx={{ fontSize: 32, color: 'text.secondary', mb: 1 }} />
                    <Typography variant="body2" gutterBottom>
                      {videoDropzone.isDragActive ? 'Drop video files here' : 'Drag & drop or click'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      MP4, MOV, AVI, WEBM (Max 5 files)
                    </Typography>
                  </Box>

                  {/* Video Files List */}
                  {uploadState.videoFiles.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Uploaded Files ({uploadState.videoFiles.length})
                      </Typography>
                      {uploadState.videoFiles.map((file, index) => (
                        <Paper key={index} sx={{ p: 1, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getFileIcon(file)}
                          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                            <Typography variant="body2" noWrap>{file.name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {formatFileSize(file.size)}
                            </Typography>
                          </Box>
                          <IconButton
                            size="small"
                            onClick={() => removeFile('videoFiles', index)}
                            disabled={uploadState.uploading}
                          >
                            <Delete />
                          </IconButton>
                        </Paper>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* File Summary */}
          {getTotalFiles() > 0 && (
            <Card sx={{ mt: 3, mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Upload Summary
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  {uploadState.pitchDeckFiles.length > 0 && (
                    <Chip
                      icon={<Slideshow />}
                      label={`${uploadState.pitchDeckFiles.length} Pitch Deck${uploadState.pitchDeckFiles.length > 1 ? 's' : ''}`}
                      color="primary"
                      variant="outlined"
                    />
                  )}
                  {uploadState.audioFiles.length > 0 && (
                    <Chip
                      icon={<AudioFile />}
                      label={`${uploadState.audioFiles.length} Audio File${uploadState.audioFiles.length > 1 ? 's' : ''}`}
                      color="secondary"
                      variant="outlined"
                    />
                  )}
                  {uploadState.videoFiles.length > 0 && (
                    <Chip
                      icon={<VideoFile />}
                      label={`${uploadState.videoFiles.length} Video File${uploadState.videoFiles.length > 1 ? 's' : ''}`}
                      color="success"
                      variant="outlined"
                    />
                  )}
                  <Chip
                    label={`Total: ${getTotalFiles()} files`}
                    color="info"
                    variant="filled"
                  />
                </Box>
              </CardContent>
            </Card>
          )}

          {/* Upload Progress */}
          {uploadState.uploading && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Processing Your Startup...
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={uploadState.progress}
                  sx={{ mb: 2, height: 8, borderRadius: 4 }}
                />
                <Typography variant="body2" color="text.secondary" align="center">
                  {uploadState.progress}% - AI agents are analyzing your startup data
                </Typography>
                <Typography variant="caption" display="block" align="center" sx={{ mt: 1 }}>
                  This may take 2-3 minutes depending on file size and complexity
                </Typography>
              </CardContent>
            </Card>
          )}

          {/* Upload Button */}
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 3 }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleUpload}
              disabled={uploadState.uploading || getTotalFiles() === 0}
              startIcon={uploadState.uploading ? null : <CloudUpload />}
              sx={{ minWidth: 200 }}
            >
              {uploadState.uploading ? 'Processing...' : 'Start AI Analysis'}
            </Button>
            
            {getTotalFiles() > 0 && (
              <Button
                variant="outlined"
                size="large"
                onClick={handleReset}
                disabled={uploadState.uploading}
              >
                Clear All Files
              </Button>
            )}
          </Box>
        </>
      )}
    </Container>
  );
};

export default Upload;
