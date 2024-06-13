# Data Preprocessing
This is a data-preprocessing tool to analyze EEG, ECG, and Audio data for sleep anlysis 

## How to use it

1. Clone the repo
2. ```pip install -r requirements.txt```
3. Run ```main.py```
4. Set up path and parameters and extract the data

## EEG Processing
EEG singals are analyzed using time window method and the *window duration* and *time step* are parameterized. 

The feautres that are extracted that are extracted includes:

1. Time Domain Featueres
   - Mean
   - Variance
   - Skewness
   - Kurtosis

2. Frequnecy Domain Powers
   - Band powers of signals
     - **Delta** (0.5 ~ 4 Hz): Deep sleep, unconscious state

     - **Theta** (4 ~ 8 Hz): Light sleep, drowsiness

     - **Alpha** (8 ~ 13 Hz): Relaxed awake but not actively processing information
     - **Beta** (13 ~ 30 Hz): Active, alert mental state

     - **Gamma** (30 ~ 100 Hz): High-level information processing, and cognitive functioning
  
## ECG Processing
Before the ECG signal is processed, a bandpass filter is applied. The *low cut off* and *high cut off* are parameterized.

The features that are extracted includes:
- **Heart Rate (BPM)**: Time intervals between R-peaks
- **RR Interval**: Time between successive R-peaks 
- **Heart Rate Variability**: This can be used to understand automatic nervous system activity
- **P Wave Duration**: Time interval of the P wave
- **QRS Duration**: Time interval of the QRS complex
- **T Wave Duration**: Time interval of the T wave
- **PR Interval**: Time interval from the start of the P wave to the start of the QRS complex 
- **QT Interval**: Time interval from the start of the QRS complex to the end of the T wave

## Audio Processing
Similar to the EEG data, a bandpass filter is applied to the signal before processing, and the *low cut off* and *high cut off* are parameterized.

The features extracted includes:
- **Zero Crossing Rate (ZCR)**: The rate at which the signal changes sign, indicating the frequency of signal oscillation.
- **Root Mean Square (RMS) Energy**: A measure of the signal’s power, representing the energy content.
- **Spectral Centroid and Bandwidth**: The center of mass of the spectrum and the range of frequencies present
- **Spectral Rolloff Frequency**: The frequency that contains the majority of the total energy spectrum.
- **Mel-Frequency Cepstral Coefficients (MFCC)**: A representation of the short-term power spectrum of a sound

## Data 
Unzip the Audio_data zip file to use collected data. The data consists of 1855 videos of 10-seconnd long snoring videos and 215 10-second long traffic videos. 

https://drive.google.com/file/d/1F4Xd00HNIcBcZj_OByiXYHyqZQNFQ9vC/view?usp=sharing








