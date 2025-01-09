// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDzJUlxaiSEvxRLhZBCM9_dzCc9vl_3v3w",
  authDomain: "quantizedai-df033.firebaseapp.com",
  projectId: "quantizedai-df033",
  storageBucket: "quantizedai-df033.firebasestorage.app",
  messagingSenderId: "910896934870",
  appId: "1:910896934870:web:2f2e5e346b8ba031d4fe77",
  measurementId: "G-QSLREPJFXH"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
// Initialize Firebase Analytics only if supported
let analytics;
isSupported().then((supported) => {
    if (supported) {
        analytics = getAnalytics(app);
    }
});

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();