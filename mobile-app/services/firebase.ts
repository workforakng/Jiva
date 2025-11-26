 import { 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User as FirebaseUser
} from 'firebase/auth';
import { 
  collection, 
  doc, 
  getDoc, 
  getDocs, 
  setDoc, 
  updateDoc,
  query,
  where,
  orderBy,
  DocumentData
} from 'firebase/firestore';
import { ref, uploadBytesResumable, getDownloadURL } from 'firebase/storage';
import { auth, db, storage } from '../config/firebase.config';
import { User, HealthRecord } from '../constants/Types';

// Auth Services
export const authService = {
  // Register new user
  register: async (email: string, password: string, userData: Partial<User>) => {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // Create user document in Firestore
      await setDoc(doc(db, 'users', user.uid), {
        id: user.uid,
        email: user.email,
        ...userData,
        createdAt: new Date().toISOString(),
      });
      
      return user;
    } catch (error: any) {
      throw new Error(error.message);
    }
  },

  // Login user
  login: async (email: string, password: string) => {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      return userCredential.user;
    } catch (error: any) {
      throw new Error(error.message);
    }
  },

  // Logout user
  logout: async () => {
    try {
      await signOut(auth);
    } catch (error: any) {
      throw new Error(error.message);
    }
  },

  // Auth state observer
  onAuthChange: (callback: (user: FirebaseUser | null) => void) => {
    return onAuthStateChanged(auth, callback);
  },

  // Get current user
  getCurrentUser: () => {
    return auth.currentUser;
  },
};

// User Services
export const userService = {
  // Get user profile
  getProfile: async (userId: string): Promise<User | null> => {
    try {
      const userDoc = await getDoc(doc(db, 'users', userId));
      if (userDoc.exists()) {
        return userDoc.data() as User;
      }
      return null;
    } catch (error: any) {
      throw new Error(error.message);
    }
  },

  // Update user profile
  updateProfile: async (userId: string, data: Partial<User>) => {
    try {
      await updateDoc(doc(db, 'users', userId), {
        ...data,
        updatedAt: new Date().toISOString(),
      });
    } catch (error: any) {
      throw new Error(error.message);
    }
  },
};

// Health Records Services
export const healthRecordsService = {
  // Get all health records for a user
  getRecords: async (userId: string): Promise<HealthRecord[]> => {
    try {
      const q = query(
        collection(db, 'healthRecords'),
        where('userId', '==', userId),
        orderBy('date', 'desc')
      );
      
      const querySnapshot = await getDocs(q);
      const records: HealthRecord[] = [];
      
      querySnapshot.forEach((doc) => {
        records.push({ id: doc.id, ...doc.data() } as HealthRecord);
      });
      
      return records;
    } catch (error: any) {
      throw new Error(error.message);
    }
  },

  // Get single health record
  getRecordById: async (recordId: string): Promise<HealthRecord | null> => {
    try {
      const recordDoc = await getDoc(doc(db, 'healthRecords', recordId));
      if (recordDoc.exists()) {
        return { id: recordDoc.id, ...recordDoc.data() } as HealthRecord;
      }
      return null;
    } catch (error: any) {
      throw new Error(error.message);
    }
  },

  // Create new health record
  createRecord: async (record: Omit<HealthRecord, 'id'>) => {
    try {
      const recordRef = doc(collection(db, 'healthRecords'));
      await setDoc(recordRef, {
        ...record,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
      return recordRef.id;
    } catch (error: any) {
      throw new Error(error.message);
    }
  },
};

// Storage Services
export const storageService = {
  // Upload document to Firebase Storage
  uploadDocument: async (
    uri: string,
    fileName: string,
    onProgress?: (progress: number) => void
  ): Promise<string> => {
    try {
      const response = await fetch(uri);
      const blob = await response.blob();
      
      const storageRef = ref(storage, `documents/${Date.now()}_${fileName}`);
      const uploadTask = uploadBytesResumable(storageRef, blob);
      
      return new Promise((resolve, reject) => {
        uploadTask.on(
          'state_changed',
          (snapshot) => {
            const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
            onProgress?.(progress);
          },
          (error) => {
            reject(error);
          },
          async () => {
            const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
            resolve(downloadURL);
          }
        );
      });
    } catch (error: any) {
      throw new Error(error.message);
    }
  },
};
