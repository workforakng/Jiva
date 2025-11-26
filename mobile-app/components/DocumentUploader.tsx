 
import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as DocumentPicker from 'expo-document-picker';
import * as ImagePicker from 'expo-image-picker';
import Colors from '../constants/Colors';

interface DocumentUploaderProps {
  onDocumentSelected: (document: any) => void;
  loading?: boolean;
}

export default function DocumentUploader({ onDocumentSelected, loading = false }: DocumentUploaderProps) {
  const [selectedFile, setSelectedFile] = useState<any>(null);

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf', 'image/*'],
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const file = result.assets[0];
        setSelectedFile(file);
        onDocumentSelected(file);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick document');
      console.error(error);
    }
  };

  const pickImage = async () => {
    // Request camera permissions
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert('Permission Denied', 'Camera permission is required to take photos');
      return;
    }

    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const file = result.assets[0];
        setSelectedFile(file);
        onDocumentSelected(file);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to take photo');
      console.error(error);
    }
  };

  const selectFromGallery = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert('Permission Denied', 'Gallery permission is required');
      return;
    }

    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const file = result.assets[0];
        setSelectedFile(file);
        onDocumentSelected(file);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to select image');
      console.error(error);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.light.primary} />
        <Text style={styles.loadingText}>Processing document...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {selectedFile ? (
        <View style={styles.selectedFile}>
          <Ionicons name="document-text" size={48} color={Colors.light.primary} />
          <Text style={styles.fileName}>{selectedFile.name || 'Selected file'}</Text>
          <TouchableOpacity onPress={() => setSelectedFile(null)}>
            <Text style={styles.changeText}>Change file</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.uploadOptions}>
          <Text style={styles.title}>Upload Medical Document</Text>
          <Text style={styles.subtitle}>Choose how you want to add your document</Text>
          
          <TouchableOpacity style={styles.optionButton} onPress={pickImage}>
            <Ionicons name="camera" size={24} color={Colors.light.primary} />
            <Text style={styles.optionText}>Take Photo</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.optionButton} onPress={selectFromGallery}>
            <Ionicons name="images" size={24} color={Colors.light.primary} />
            <Text style={styles.optionText}>Choose from Gallery</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.optionButton} onPress={pickDocument}>
            <Ionicons name="document-attach" size={24} color={Colors.light.primary} />
            <Text style={styles.optionText}>Select PDF Document</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  uploadOptions: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: Colors.light.text,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 24,
  },
  optionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.light.cardBackground,
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  optionText: {
    fontSize: 16,
    fontWeight: '500',
    color: Colors.light.text,
    marginLeft: 16,
  },
  selectedFile: {
    alignItems: 'center',
    padding: 32,
  },
  fileName: {
    fontSize: 16,
    fontWeight: '500',
    color: Colors.light.text,
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  changeText: {
    fontSize: 14,
    color: Colors.light.primary,
    fontWeight: '500',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 16,
  },
});
