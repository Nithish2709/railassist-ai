import React from 'react';

export default function Footer({ onNavClick }) {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div>
          <strong style={{ color: '#ffffff' }}>RailAssist AI</strong> — Academic Machine Learning Railway Complaint Classifier
        </div>
        <div className="footer-disclaimer">
          <strong>Academic Prototype Notice:</strong> This project is a standalone academic demonstration 
          developed for automated text classification research. It is <em>not</em> an officially integrated Indian Railways service, 
          IRCTC portal, or RailMadad grievance management system. In case of real emergencies, dial 139 (Indian Railways Helpline) or contact RPF directly.
        </div>
        <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
          TF-IDF + Random Forest Classifier (200 Estimators) | Dataset: Hugging Face (MIT License) | Python & FastAPI + React & Vite
        </div>
      </div>
    </footer>
  );
}
