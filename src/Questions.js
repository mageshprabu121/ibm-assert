import React, { useState, useEffect } from 'react';
import './Questions.css';

const SpeechToText = ({ onTranscript }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recognizer, setRecognizer] = useState(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech Recognition API not supported');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(result => result[0].transcript)
        .join('');
      onTranscript(transcript);
    };

    recognition.onend = () => {
      if (isRecording) recognition.start();
    };

    setRecognizer(recognition);

    return () => {
      if (recognizer) {
        recognizer.stop();
        recognizer.onend = null;
      }
    };
  }, [isRecording]);

  const startRecording = () => {
    if (recognizer) {
      recognizer.start();
      setIsRecording(true);
    }
  };

  const stopRecording = () => {
    if (recognizer) {
      recognizer.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="mic-controls">
      <button className="blue-button" onClick={startRecording} disabled={isRecording}>Start Mic</button>
      <button className="blue-button" onClick={stopRecording} disabled={!isRecording}>Stop Mic</button>
    </div>
  );
};

const Questions = ({ candidateInfo }) => {
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [transcripts, setTranscripts] = useState([]);
  const [error, setError] = useState(null);
  const [isFinished, setIsFinished] = useState(false);

  const fetchQuestions = async () => {
    try {
      const response = await fetch('/sample.txt');
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.text();
      const lines = data.split('\n');
      const parsedQuestions = lines.filter(line => line.startsWith('* Question'));
      setQuestions(parsedQuestions);
    } catch (error) {
      setError(error.message);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, []);

  const handleTranscript = (transcript) => {
    setTranscripts(prev => {
      const updated = [...prev];
      updated[currentQuestionIndex] = transcript;
      return updated;
    });
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setIsFinished(false);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleFinish = async () => {
    const response = await fetch('http://127.0.0.1:8000/save-assessment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: candidateInfo.name,
        email: candidateInfo.email,
        questions: questions,
        transcripts: transcripts
      })
    });

    if (response.ok) {
      setIsFinished(true);
    } else {
      setError('Failed to save the assessment');
    }
  };

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (questions.length === 0) {
    return <div>Loading questions...</div>;
  }

  return (
    <div className="questions-container">
      <img src="https://res.cloudinary.com/dadvxtk3n/image/upload/v1724221121/ibm_logo_pwwuem.png" alt="Logo" className="logo" />
      <img src="https://res.cloudinary.com/dadvxtk3n/image/upload/v1724565404/leadspace_cjw9h6-removebg-preview_kw8yri.png" alt="Banner" className="banner" />
      <h1>AI Engineer Questions</h1>
      <div className="question-card">
        <h2>{questions[currentQuestionIndex]}</h2>
        <SpeechToText onTranscript={handleTranscript} />
        <div className="navigation-buttons">
          <button className="blue-button" onClick={handlePreviousQuestion} disabled={currentQuestionIndex === 0}>Previous</button>
          <button className="blue-button" onClick={handleNextQuestion} disabled={currentQuestionIndex === questions.length - 1}>Next</button>
          <button className="blue-button" onClick={handleFinish} disabled={isFinished || currentQuestionIndex !== questions.length - 1}>Finish</button>
        </div>
      </div>
    </div>
  );
};

export default Questions;

