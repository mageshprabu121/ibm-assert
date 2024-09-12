// import React, { useState } from 'react';
// import Questions from './Questions';
// import './App.css';

// const App = () => {
//   const [candidateInfo, setCandidateInfo] = useState({ name: '', email: '' });
//   const [isAssessmentStarted, setIsAssessmentStarted] = useState(false);

//   const handleInputChange = (e) => {
//     setCandidateInfo({
//       ...candidateInfo,
//       [e.target.name]: e.target.value
//     });
//   };

//   const handleSubmit = () => {
//     if (candidateInfo.name && candidateInfo.email) {
//       setIsAssessmentStarted(true);
//     } else {
//       alert('Please enter your name and email.');
//     }
//   };

//   return (
//     <div className="app-container">
//       {!isAssessmentStarted ? (
//         <div className="info-form">
//           <h1>Candidate Information</h1>
//           <input
//             type="text"
//             name="name"
//             placeholder="Enter your name"
//             value={candidateInfo.name}
//             onChange={handleInputChange}
//           />
//           <input
//             type="email"
//             name="email"
//             placeholder="Enter your email"
//             value={candidateInfo.email}
//             onChange={handleInputChange}
//           />
//           <button className="blue-button" onClick={handleSubmit}>Start Assessment</button>
//         </div>
//       ) : (
//         <Questions candidateInfo={candidateInfo} />
//       )}
//     </div>
//   );
// };

// export default App;

import React, { useState } from 'react';
import Questions from './Questions';
import './App.css';

const App = () => {
  const [candidateInfo, setCandidateInfo] = useState({ name: '', email: '' });
  const [isAssessmentStarted, setIsAssessmentStarted] = useState(false);

  const handleInputChange = (e) => {
    setCandidateInfo({
      ...candidateInfo,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = () => {
    if (candidateInfo.name && candidateInfo.email) {
      setIsAssessmentStarted(true);
    } else {
      alert('Please enter your name and email.');
    }
  };

  return (
    <div className="app-container1">
      {!isAssessmentStarted ? (
        <div className="info-form1">
          <div className="header-container1">
            <img src="https://res.cloudinary.com/dadvxtk3n/image/upload/v1724221121/ibm_logo_pwwuem.png" alt="Logo1" className="logo1"/>
            <img src="https://res.cloudinary.com/dadvxtk3n/image/upload/v1724221306/leadspace_cjw9h6.png" alt="Banner1" className="banner1"/>
          </div>
          <h1>Candidate Information</h1>
          <input
            type="text"
            name="name"
            placeholder="Enter your name"
            value={candidateInfo.name}
            onChange={handleInputChange}
          />
          <input
            type="email"
            name="email"
            placeholder="Enter your email"
            value={candidateInfo.email}
            onChange={handleInputChange}
          />
          <button className="blue-button1" onClick={handleSubmit}>Start Assessment</button>
        </div>
      ) : (
        <Questions candidateInfo={candidateInfo} />
      )}
    </div>
  );
};

export default App;
