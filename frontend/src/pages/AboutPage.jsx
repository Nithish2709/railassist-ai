import React from 'react';

export default function AboutPage({ categories }) {
  return (
    <div className="about-container" style={{ maxWidth: '960px', margin: '0 auto' }}>
      <div className="section-header" style={{ margin: '1rem 0 2.5rem' }}>
        <h1 className="section-title">About RailAssist AI</h1>
        <p className="section-subtitle">
          Academic documentation on dataset acquisition, label mapping methodology, machine learning architecture, and empirical held-out evaluation.
        </p>
      </div>

      {/* 1. Project Objective */}
      <section className="card" style={{ marginBottom: '2rem' }}>
        <h2 className="card-title" style={{ fontSize: '1.4rem', borderBottom: '1px solid #1e3557', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
          1. Project Objective & Scope
        </h2>
        <p className="card-text" style={{ marginBottom: '1rem' }}>
          The objective of <strong>RailAssist AI</strong> is to provide an automated, text-based machine learning solution for classifying railway passenger grievances. In high-volume passenger transport networks like Indian Railways, grievances submitted via social media or web portals span multiple operational departments — ranging from sanitation and catering to mechanical carriage repair and security.
        </p>
        <p className="card-text" style={{ marginBottom: '1rem' }}>
          By processing plain-English complaint descriptions, RailAssist AI predicts the underlying operational issue and deterministically routes the ticket to the responsible department without human triage delays.
        </p>
        <div className="alert-box info" style={{ margin: '1rem 0 0' }}>
          <div className="alert-icon">📌</div>
          <div className="alert-text">
            <strong>Scope Boundary:</strong> This application focuses strictly on <em>text-based multiclass classification</em>. In alignment with academic guidelines, it intentionally omits extraneous features such as image recognition, biometric tracking, payment handling, or autonomous agent frameworks.
          </div>
        </div>
      </section>

      {/* 2. Dataset Acquisition & Provenance */}
      <section className="card" style={{ marginBottom: '2rem' }}>
        <h2 className="card-title" style={{ fontSize: '1.4rem', borderBottom: '1px solid #1e3557', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
          2. Dataset Acquisition & Provenance
        </h2>
        <p className="card-text" style={{ marginBottom: '1rem' }}>
          The system was trained on the public Indian Railways tweet dataset curated by Faiz Mubeen, hosted on Hugging Face:
        </p>
        <div className="data-table-wrap">
          <table className="data-table">
            <tbody>
              <tr>
                <th>Dataset Name</th>
                <td><code>faizmubeen/indian_railways_complaint_tweets</code></td>
              </tr>
              <tr>
                <th>Repository URL</th>
                <td><a href="https://huggingface.co/datasets/faizmubeen/indian_railways_complaint_tweets" target="_blank" rel="noreferrer">Hugging Face Dataset Portal</a></td>
              </tr>
              <tr>
                <th>Revision / Commit SHA</th>
                <td><code>f2a3e5f9491324a9acaf4210558ad413583860c5</code></td>
              </tr>
              <tr>
                <th>License</th>
                <td><strong>MIT License</strong> (Permissive academic & commercial use)</td>
              </tr>
              <tr>
                <th>Raw Record Count</th>
                <td><strong>4,535 records</strong> (2,615 complaints, 1,920 non-complaints)</td>
              </tr>
              <tr>
                <th>Raw SHA-256 Hash</th>
                <td><code>cf8fb6b9743e7cfdb51d26358149799cc1719770e89979992de2dfe5c9ad891c</code></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* 3. Data Cleaning and Label Mapping */}
      <section className="card" style={{ marginBottom: '2rem' }}>
        <h2 className="card-title" style={{ fontSize: '1.4rem', borderBottom: '1px solid #1e3557', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
          3. Data Cleaning & Label Mapping Methodology
        </h2>
        <p className="card-text" style={{ marginBottom: '1rem' }}>
          To prevent data leakage and guarantee scientific validity, the raw dataset underwent rigorous preprocessing:
        </p>
        <ul style={{ paddingLeft: '1.5rem', color: '#94a3b8', lineHeight: '1.8', marginBottom: '1.25rem' }}>
          <li><strong>Exclusion of Non-Complaints:</strong> All 1,920 non-complaint records (travel photos, news updates, generic praise) were excluded from supervised complaint training.</li>
          <li><strong>Exclusion of Vague Catch-Alls:</strong> Highly ambiguous labels (e.g. <code>service</code> [180], <code>facility</code> [142], <code>miscellaneous</code> [177], <code>others</code> [68], <code>political</code> [52]) were excluded to prevent turning <code>Passenger Grievance</code> into a noisy catch-all category.</li>
          <li><strong>Exclusion of Unsupported / Scarcity Categories:</strong> <code>Engineering</code> (0 raw records) and <code>Medical Assistance</code> (only 11 raw records; 0.6% representation) were removed to ensure all trained categories possess solid statistical representation.</li>
          <li><strong>Text Normalization:</strong> Stripped HTML entities, decomposed Unicode ligatures (NFKC), removed URLs, and collapsed whitespace.</li>
          <li><strong>Deduplication:</strong> 9 duplicate text records were pruned, yielding <strong>1,949 cleaned, verified complaints</strong> across 8 active target categories.</li>
        </ul>

        <h3 style={{ fontSize: '1.1rem', color: '#ffffff', marginBottom: '0.75rem' }}>Eight Target Operational Categories</h3>
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Responsible Department</th>
                <th>Cleaned Records</th>
                <th>Share</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Operations & Traffic</strong></td>
                <td>Operating Department (Traffic & Scheduling)</td>
                <td>785</td>
                <td>40.3%</td>
                <td><span className="cat-badge supported">Supported</span></td>
              </tr>
              <tr>
                <td><strong>Passenger Grievance</strong></td>
                <td>Commercial Department (Public Grievance Cell)</td>
                <td>401</td>
                <td>20.6%</td>
                <td><span className="cat-badge supported">Supported</span></td>
              </tr>
              <tr>
                <td><strong>Housekeeping</strong></td>
                <td>Environment & Housekeeping Management (EnHM) / OBHS</td>
                <td>328</td>
                <td>16.8%</td>
                <td><span className="cat-badge supported">Supported</span></td>
              </tr>
              <tr>
                <td><strong>Security</strong></td>
                <td>Security Department (Railway Protection Force - RPF)</td>
                <td>141</td>
                <td>7.2%</td>
                <td><span className="cat-badge supported">Supported</span></td>
              </tr>
              <tr>
                <td><strong>Electrical</strong></td>
                <td>Electrical Engineering Department (Train Lighting & AC)</td>
                <td>95</td>
                <td>4.9%</td>
                <td><span className="cat-badge supported">Supported</span></td>
              </tr>
              <tr>
                <td><strong>Catering</strong></td>
                <td>Catering & Vending Services (IRCTC / Commercial)</td>
                <td>88</td>
                <td>4.5%</td>
                <td><span className="cat-badge supported">Supported</span></td>
              </tr>
              <tr>
                <td><strong>Coach Maintenance</strong></td>
                <td>Mechanical Engineering Department (Carriage & Wagon)</td>
                <td>66</td>
                <td>3.4%</td>
                <td><span className="cat-badge supported">Supported</span></td>
              </tr>
              <tr>
                <td><strong>Water & Sanitation</strong></td>
                <td>Water Supply & Sanitation Department</td>
                <td>45</td>
                <td>2.3%</td>
                <td><span className="cat-badge supported">Supported</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* 4. Model Architecture & Pipeline */}
      <section className="card" style={{ marginBottom: '2rem' }}>
        <h2 className="card-title" style={{ fontSize: '1.4rem', borderBottom: '1px solid #1e3557', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
          4. Machine Learning Pipeline Architecture
        </h2>
        <p className="card-text" style={{ marginBottom: '1rem' }}>
          The machine learning pipeline couples feature extraction and decision ensemble into a unified, reproducible <code>scikit-learn Pipeline</code>:
        </p>
        <div style={{ background: '#0a1525', padding: '1.25rem', borderRadius: '8px', border: '1px solid #1e3557', fontFamily: 'monospace', fontSize: '0.9rem', color: '#38bdf8', marginBottom: '1.5rem' }}>
          Raw Complaint Text ➔ Text Normalization ➔ TF-IDF Vectorizer (1-2 ngrams, 5000 feats) ➔ RandomForestClassifier (200 trees) ➔ Predicted Category ➔ Deterministic Department Router
        </div>
        <ul style={{ paddingLeft: '1.5rem', color: '#94a3b8', lineHeight: '1.8' }}>
          <li><strong>TF-IDF Vectorization:</strong> Unigrams and bigrams (<code>ngram_range=(1,2)</code>), sublinear term frequency scaling, 5,000 maximum vocabulary features, <code>min_df=2</code>. Strictly fitted on the training split only to prevent data leakage.</li>
          <li><strong>Random Forest Classifier (Primary):</strong> 200 estimators, balanced subsample class weighting (<code>class_weight="balanced_subsample"</code>), square-root feature subset splitting, fixed seed 42.</li>
          <li><strong>Logistic Regression (Baseline):</strong> Trained on identical 80/20 train/test split with balanced class weighting for objective performance benchmarking.</li>
        </ul>
      </section>

      {/* 5. Empirical Evaluation Results */}
      <section className="card" style={{ marginBottom: '2rem' }}>
        <h2 className="card-title" style={{ fontSize: '1.4rem', borderBottom: '1px solid #1e3557', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
          5. Measured Evaluation Results on Held-Out Test Set (390 Samples)
        </h2>
        <p className="card-text" style={{ marginBottom: '1rem' }}>
          All performance metrics are calculated strictly on the held-out test split (20% stratified, seed 42) — <em>never</em> on training data:
        </p>

        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Global Metric</th>
                <th>Random Forest (Primary Model)</th>
                <th>Logistic Regression (Baseline)</th>
                <th>Observed Difference</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Overall Test Accuracy</strong></td>
                <td><span className="metric-pill">75.38%</span></td>
                <td><span className="metric-pill">80.51%</span></td>
                <td style={{ color: '#38bdf8' }}>+5.13% (Baseline higher)</td>
              </tr>
              <tr>
                <td><strong>Macro-Averaged F1 Score</strong></td>
                <td><span className="metric-pill">0.5670</span></td>
                <td><span className="metric-pill">0.6827</span></td>
                <td style={{ color: '#38bdf8' }}>+0.1157 (Baseline higher)</td>
              </tr>
              <tr>
                <td><strong>Weighted-Averaged F1 Score</strong></td>
                <td><span className="metric-pill">0.7255</span></td>
                <td><span className="metric-pill">0.7957</span></td>
                <td style={{ color: '#38bdf8' }}>+0.0702 (Baseline higher)</td>
              </tr>
              <tr>
                <td><strong>Mean Confidence Score</strong></td>
                <td><span className="metric-pill">60.04%</span></td>
                <td><span className="metric-pill">39.15%</span></td>
                <td style={{ color: '#f59e0b' }}>+20.89% (Random Forest more decisive)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h3 style={{ fontSize: '1.1rem', color: '#ffffff', margin: '1.5rem 0 0.75rem' }}>Per-Class Metrics on Test Data (Random Forest)</h3>
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Test Support</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-Score</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Operations & Traffic</strong></td>
                <td>157</td>
                <td>0.829</td>
                <td>0.955</td>
                <td><strong>0.888</strong></td>
              </tr>
              <tr>
                <td><strong>Passenger Grievance</strong></td>
                <td>80</td>
                <td>0.670</td>
                <td>0.788</td>
                <td><strong>0.724</strong></td>
              </tr>
              <tr>
                <td><strong>Housekeeping</strong></td>
                <td>66</td>
                <td>0.676</td>
                <td>0.758</td>
                <td><strong>0.714</strong></td>
              </tr>
              <tr>
                <td><strong>Electrical</strong></td>
                <td>19</td>
                <td>0.706</td>
                <td>0.632</td>
                <td><strong>0.667</strong></td>
              </tr>
              <tr>
                <td><strong>Catering</strong></td>
                <td>18</td>
                <td>0.769</td>
                <td>0.556</td>
                <td><strong>0.645</strong></td>
              </tr>
              <tr>
                <td><strong>Water & Sanitation</strong></td>
                <td>9</td>
                <td>0.750</td>
                <td>0.333</td>
                <td><strong>0.462</strong></td>
              </tr>
              <tr>
                <td><strong>Security</strong></td>
                <td>28</td>
                <td>0.833</td>
                <td>0.179</td>
                <td><strong>0.294</strong></td>
              </tr>
              <tr>
                <td><strong>Coach Maintenance</strong></td>
                <td>13</td>
                <td>1.000</td>
                <td>0.077</td>
                <td><strong>0.143</strong></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="alert-box info" style={{ margin: '1.5rem 0 0' }}>
          <div className="alert-icon">📊</div>
          <div className="alert-text">
            <strong>Honest Comparison Analysis:</strong> In high-dimensional sparse TF-IDF spaces (5,000 dimensions), 
            linear classifiers like Logistic Regression find smooth hyperplane boundaries, outperforming axis-aligned decision tree partitions on minority classes (80.51% vs 75.38%). 
            However, Random Forest produces higher individual voting agreement across its 200 trees (60.0% vs 39.2%).
          </div>
        </div>
      </section>

      {/* 6. Honest Limitations & Transparency */}
      <section className="card" style={{ marginBottom: '2.5rem' }}>
        <h2 className="card-title" style={{ fontSize: '1.4rem', borderBottom: '1px solid #1e3557', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
          6. Model Scope & Limitations
        </h2>
        <ul style={{ paddingLeft: '1.5rem', color: '#94a3b8', lineHeight: '1.8' }}>
          <li>
            <strong>Streamlined 8 Operational Categories:</strong> Per data integrity requirements, categories lacking sufficient training support (Medical Assistance [11 records] and Engineering [0 records]) were pruned to ensure model reliability.
          </li>
          <li>
            <strong>Probability Calibration:</strong> The output confidence score represents the fraction of decision trees voting for a class. In scikit-learn's Random Forest, leaf probabilities are empirical tree-voting proportions rather than calibrated Bayesian posterior probabilities.
          </li>
          <li>
            <strong>Academic Scope:</strong> Not connected to live Indian Railways dispatch systems. Emergency life-safety issues require immediate human helpline contact (139 or RPF).
          </li>
        </ul>
      </section>
    </div>
  );
}
