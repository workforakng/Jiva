 
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Image,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import * as DocumentPicker from 'expo-document-picker';
import * as ImagePicker from 'expo-image-picker';
import Colors from '../../constants/Colors';
import { storageService, healthRecordsService, authService } from '../../services/firebase';
import apiService from '../../services/api';

type UploadStage = 'select' | 'preview' | 'processing' | 'success' | 'error';

interface SelectedFile {
  uri: string;
  name: string;
  type: string;
  size?: number;
}

export default function UploadScreen() {
  const [uploadStage, setUploadStage] = useState<UploadStage>('select');
  const [selectedFile, setSelectedFile] = useState<SelectedFile | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStatus, setProcessingStatus] = useState('');
  const [extractedData, setExtractedData] = useState<any>(null);

  // Reset to initial state
  const resetUpload = () => {
    setUploadStage('select');
    setSelectedFile(null);
    setUploadProgress(0);
    setProcessingStatus('');
    setExtractedData(null);
  };

  // Pick image from camera
  const pickImageFromCamera = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert(
        'Permission Denied',
        'Camera permission is required to take photos of medical documents.'
      );
      return;
    }

    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        quality: 0.9,
        aspect: [4, 3],
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const file = result.assets[0];
        setSelectedFile({
          uri: file.uri,
          name: `medical_document_${Date.now()}.jpg`,
          type: 'image/jpeg',
        });
        setUploadStage('preview');
      }
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Error', 'Failed to take photo. Please try again.');
    }
  };

  // Pick image from gallery
  const pickImageFromGallery = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (status !== 'granted') {
      Alert.alert(
        'Permission Denied',
        'Gallery permission is required to select photos.'
      );
      return;
    }

    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        quality: 0.9,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const file = result.assets[0];
        setSelectedFile({
          uri: file.uri,
          name: file.fileName || `medical_document_${Date.now()}.jpg`,
          type: 'image/jpeg',
        });
        setUploadStage('preview');
      }
    } catch (error) {
      console.error('Error selecting image:', error);
      Alert.alert('Error', 'Failed to select image. Please try again.');
    }
  };

  // Pick PDF document
  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf', 'image/*'],
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const file = result.assets[0];
        setSelectedFile({
          uri: file.uri,
          name: file.name,
          type: file.mimeType || 'application/pdf',
          size: file.size,
        });
        setUploadStage('preview');
      }
    } catch (error) {
      console.error('Error picking document:', error);
      Alert.alert('Error', 'Failed to pick document. Please try again.');
    }
  };

  // Upload and process document
  const uploadDocument = async () => {
    if (!selectedFile) return;

    setUploadStage('processing');
    setProcessingStatus('Uploading document...');

    try {
      const user = authService.getCurrentUser();
      if (!user) {
        throw new Error('User not authenticated');
      }

      // Step 1: Upload to Firebase Storage
      const downloadURL = await storageService.uploadDocument(
        selectedFile.uri,
        selectedFile.name,
        (progress) => {
          setUploadProgress(progress);
          if (progress < 100) {
            setProcessingStatus(`Uploading... ${Math.round(progress)}%`);
          }
        }
      );

      // Step 2: Process with OCR (simulated for now)
      setProcessingStatus('Processing document with AI...');
      await new Promise((resolve) => setTimeout(resolve, 2000));

      setProcessingStatus('Extracting biomarkers...');
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Step 3: Create mock extracted data (replace with actual API call)
      const mockExtractedData = {
        type: 'Blood Test',
        facility: 'City Diagnostics Lab',
        date: new Date().toISOString().split('T')[0],
        biomarkers: {
          hemoglobin: {
            value: 14.2,
            unit: 'g/dL',
            range: '12.0-16.0',
            status: 'normal' as const,
          },
          bloodSugar: {
            value: 95,
            unit: 'mg/dL',
            range: '70-100',
            status: 'normal' as const,
          },
          cholesterol: {
            value: 180,
            unit: 'mg/dL',
            range: '<200',
            status: 'normal' as const,
          },
        },
      };

      // Step 4: Save to Firestore
      setProcessingStatus('Saving to your health records...');
      await healthRecordsService.createRecord({
        userId: user.uid,
        ...mockExtractedData,
        originalDocument: selectedFile.name,
        documentUrl: downloadURL,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });

      setExtractedData(mockExtractedData);
      setUploadStage('success');
    } catch (error: any) {
      console.error('Upload error:', error);
      setUploadStage('error');
      Alert.alert('Upload Failed', error.message || 'Please try again.');
    }
  };

  // Render upload options
  const renderSelectStage = () => (
    <View style={styles.selectContainer}>
      <View style={styles.iconHeader}>
        <Ionicons name="cloud-upload" size={64} color={Colors.light.primary} />
      </View>
      
      <Text style={styles.title}>Upload Medical Document</Text>
      <Text style={styles.subtitle}>
        Take a photo or select a file from your device
      </Text>

      <View style={styles.optionsContainer}>
        <TouchableOpacity style={styles.optionCard} onPress={pickImageFromCamera}>
          <View style={styles.optionIcon}>
            <Ionicons name="camera" size={32} color={Colors.light.primary} />
          </View>
          <Text style={styles.optionTitle}>Take Photo</Text>
          <Text style={styles.optionDescription}>
            Capture document with camera
          </Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.optionCard} onPress={pickImageFromGallery}>
          <View style={styles.optionIcon}>
            <Ionicons name="images" size={32} color={Colors.light.secondary} />
          </View>
          <Text style={styles.optionTitle}>Choose from Gallery</Text>
          <Text style={styles.optionDescription}>
            Select from your photos
          </Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.optionCard} onPress={pickDocument}>
          <View style={styles.optionIcon}>
            <Ionicons name="document-attach" size={32} color={Colors.light.accent} />
          </View>
          <Text style={styles.optionTitle}>Select PDF</Text>
          <Text style={styles.optionDescription}>
            Upload PDF document
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.infoCard}>
        <Ionicons name="information-circle" size={20} color={Colors.light.primary} />
        <Text style={styles.infoText}>
          Supported formats: JPG, PNG, PDF. Max size: 10MB
        </Text>
      </View>
    </View>
  );

  // Render preview stage
  const renderPreviewStage = () => (
    <View style={styles.previewContainer}>
      <Text style={styles.title}>Preview Document</Text>
      <Text style={styles.subtitle}>Review before uploading</Text>

      {selectedFile && (
        <>
          {selectedFile.type.startsWith('image/') ? (
            <Image source={{ uri: selectedFile.uri }} style={styles.previewImage} />
          ) : (
            <View style={styles.pdfPreview}>
              <Ionicons name="document-text" size={64} color={Colors.light.primary} />
              <Text style={styles.pdfName}>{selectedFile.name}</Text>
              {selectedFile.size && (
                <Text style={styles.pdfSize}>
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </Text>
              )}
            </View>
          )}

          <View style={styles.fileInfo}>
            <View style={styles.fileInfoRow}>
              <Ionicons name="document" size={20} color="#6B7280" />
              <Text style={styles.fileInfoText}>{selectedFile.name}</Text>
            </View>
            {selectedFile.type && (
              <View style={styles.fileInfoRow}>
                <Ionicons name="pricetag" size={20} color="#6B7280" />
                <Text style={styles.fileInfoText}>{selectedFile.type}</Text>
              </View>
            )}
          </View>

          <View style={styles.buttonContainer}>
            <TouchableOpacity
              style={[styles.button, styles.secondaryButton]}
              onPress={resetUpload}
            >
              <Text style={styles.secondaryButtonText}>Cancel</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.primaryButton]}
              onPress={uploadDocument}
            >
              <Text style={styles.primaryButtonText}>Upload & Process</Text>
            </TouchableOpacity>
          </View>
        </>
      )}
    </View>
  );

  // Render processing stage
  const renderProcessingStage = () => (
    <View style={styles.processingContainer}>
      <View style={styles.processingContent}>
        <ActivityIndicator size="large" color={Colors.light.primary} />
        <Text style={styles.processingTitle}>Processing Document</Text>
        <Text style={styles.processingStatus}>{processingStatus}</Text>
        
        <View style={styles.progressBarContainer}>
          <View style={[styles.progressBar, { width: `${uploadProgress}%` }]} />
        </View>
        <Text style={styles.progressText}>{Math.round(uploadProgress)}%</Text>

        <View style={styles.processingSteps}>
          <View style={styles.stepItem}>
            <Ionicons
              name={uploadProgress > 30 ? 'checkmark-circle' : 'ellipse-outline'}
              size={24}
              color={uploadProgress > 30 ? Colors.light.success : '#D1D5DB'}
            />
            <Text style={styles.stepText}>Uploading</Text>
          </View>
          
          <View style={styles.stepItem}>
            <Ionicons
              name={uploadProgress > 60 ? 'checkmark-circle' : 'ellipse-outline'}
              size={24}
              color={uploadProgress > 60 ? Colors.light.success : '#D1D5DB'}
            />
            <Text style={styles.stepText}>OCR Processing</Text>
          </View>
          
          <View style={styles.stepItem}>
            <Ionicons
              name={uploadProgress > 90 ? 'checkmark-circle' : 'ellipse-outline'}
              size={24}
              color={uploadProgress > 90 ? Colors.light.success : '#D1D5DB'}
            />
            <Text style={styles.stepText}>Extracting Data</Text>
          </View>
        </View>
      </View>
    </View>
  );

  // Render success stage
  const renderSuccessStage = () => (
    <View style={styles.successContainer}>
      <View style={styles.successIcon}>
        <Ionicons name="checkmark-circle" size={80} color={Colors.light.success} />
      </View>
      
      <Text style={styles.successTitle}>Upload Successful!</Text>
      <Text style={styles.successSubtitle}>
        Your health record has been processed and saved
      </Text>

      {extractedData && (
        <View style={styles.extractedDataCard}>
          <Text style={styles.extractedDataTitle}>Extracted Information</Text>
          
          <View style={styles.dataRow}>
            <Text style={styles.dataLabel}>Type:</Text>
            <Text style={styles.dataValue}>{extractedData.type}</Text>
          </View>
          
          <View style={styles.dataRow}>
            <Text style={styles.dataLabel}>Facility:</Text>
            <Text style={styles.dataValue}>{extractedData.facility}</Text>
          </View>
          
          <View style={styles.dataRow}>
            <Text style={styles.dataLabel}>Date:</Text>
            <Text style={styles.dataValue}>
              {new Date(extractedData.date).toLocaleDateString('en-IN')}
            </Text>
          </View>
          
          <View style={styles.dataRow}>
            <Text style={styles.dataLabel}>Biomarkers:</Text>
            <Text style={styles.dataValue}>
              {Object.keys(extractedData.biomarkers).length} detected
            </Text>
          </View>
        </View>
      )}

      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, styles.secondaryButton]}
          onPress={resetUpload}
        >
          <Text style={styles.secondaryButtonText}>Upload Another</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.primaryButton]}
          onPress={() => {
            resetUpload();
            router.push('/timeline');
          }}
        >
          <Text style={styles.primaryButtonText}>View Timeline</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  // Render error stage
  const renderErrorStage = () => (
    <View style={styles.errorContainer}>
      <View style={styles.errorIcon}>
        <Ionicons name="close-circle" size={80} color={Colors.light.error} />
      </View>
      
      <Text style={styles.errorTitle}>Upload Failed</Text>
      <Text style={styles.errorSubtitle}>
        Something went wrong while processing your document
      </Text>

      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, styles.primaryButton]}
          onPress={resetUpload}
        >
          <Text style={styles.primaryButtonText}>Try Again</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {uploadStage === 'select' && renderSelectStage()}
        {uploadStage === 'preview' && renderPreviewStage()}
        {uploadStage === 'processing' && renderProcessingStage()}
        {uploadStage === 'success' && renderSuccessStage()}
        {uploadStage === 'error' && renderErrorStage()}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.light.background,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
  },
  
  // Select Stage
  selectContainer: {
    padding: 20,
  },
  iconHeader: {
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: Colors.light.text,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 32,
  },
  optionsContainer: {
    marginBottom: 24,
  },
  optionCard: {
    backgroundColor: Colors.light.cardBackground,
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  optionIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  optionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: Colors.light.text,
    marginBottom: 4,
  },
  optionDescription: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#EFF6FF',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#1E40AF',
    marginLeft: 12,
  },
  
  // Preview Stage
  previewContainer: {
    padding: 20,
  },
  previewImage: {
    width: '100%',
    height: 400,
    borderRadius: 12,
    marginVertical: 20,
    backgroundColor: '#F3F4F6',
  },
  pdfPreview: {
    width: '100%',
    height: 300,
    borderRadius: 12,
    marginVertical: 20,
    backgroundColor: Colors.light.cardBackground,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: Colors.light.border,
    borderStyle: 'dashed',
  },
  pdfName: {
    fontSize: 16,
    fontWeight: '500',
    color: Colors.light.text,
    marginTop: 16,
    textAlign: 'center',
    paddingHorizontal: 20,
  },
  pdfSize: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  fileInfo: {
    backgroundColor: Colors.light.cardBackground,
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  fileInfoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  fileInfoText: {
    fontSize: 14,
    color: Colors.light.text,
    marginLeft: 12,
    flex: 1,
  },
  
  // Processing Stage
  processingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  processingContent: {
    alignItems: 'center',
    width: '100%',
  },
  processingTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: Colors.light.text,
    marginTop: 24,
  },
  processingStatus: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 8,
    textAlign: 'center',
  },
  progressBarContainer: {
    width: '100%',
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    marginTop: 24,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: Colors.light.primary,
    borderRadius: 4,
  },
  progressText: {
    fontSize: 14,
    fontWeight: '600',
    color: Colors.light.primary,
    marginTop: 8,
  },
  processingSteps: {
    width: '100%',
    marginTop: 40,
  },
  stepItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  stepText: {
    fontSize: 16,
    color: Colors.light.text,
    marginLeft: 12,
  },
  
  // Success Stage
  successContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  successIcon: {
    marginBottom: 24,
  },
  successTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: Colors.light.text,
    marginBottom: 8,
  },
  successSubtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 32,
  },
  extractedDataCard: {
    width: '100%',
    backgroundColor: Colors.light.cardBackground,
    borderRadius: 16,
    padding: 20,
    marginBottom: 32,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  extractedDataTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: Colors.light.text,
    marginBottom: 16,
  },
  dataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  dataLabel: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  dataValue: {
    fontSize: 14,
    color: Colors.light.text,
    fontWeight: '600',
  },
  
  // Error Stage
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorIcon: {
    marginBottom: 24,
  },
  errorTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: Colors.light.text,
    marginBottom: 8,
  },
  errorSubtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 32,
  },
  
  // Buttons
  buttonContainer: {
    flexDirection: 'row',
    width: '100%',
    gap: 12,
  },
  button: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryButton: {
    backgroundColor: Colors.light.primary,
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  secondaryButton: {
    backgroundColor: Colors.light.cardBackground,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  secondaryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: Colors.light.text,
  },
});
