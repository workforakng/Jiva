 
import * as SecureStore from 'expo-secure-store';

// Secure storage service for sensitive data
export const secureStorage = {
  // Save item
  async save(key: string, value: string): Promise<void> {
    try {
      await SecureStore.setItemAsync(key, value);
    } catch (error) {
      console.error('Error saving to secure storage:', error);
      throw error;
    }
  },

  // Get item
  async get(key: string): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync(key);
    } catch (error) {
      console.error('Error reading from secure storage:', error);
      return null;
    }
  },

  // Delete item
  async delete(key: string): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(key);
    } catch (error) {
      console.error('Error deleting from secure storage:', error);
      throw error;
    }
  },

  // Clear all
  async clear(): Promise<void> {
    // Note: SecureStore doesn't have a clear all method
    // You need to track keys and delete them individually
    const keys = ['userToken', 'userId', 'refreshToken'];
    await Promise.all(keys.map((key) => this.delete(key)));
  },
};

// Storage keys constants
export const STORAGE_KEYS = {
  USER_TOKEN: 'userToken',
  USER_ID: 'userId',
  REFRESH_TOKEN: 'refreshToken',
  USER_PREFERENCES: 'userPreferences',
};
