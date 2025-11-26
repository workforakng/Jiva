 
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Modal,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import Colors from '../../constants/Colors';
import TimelineCard from '../../components/TimelineCard';
import BiomarkerDisplay from '../../components/BiomarkerDisplay';
import LoadingOverlay from '../../components/LoadingOverlay';
import { healthRecordsService, authService } from '../../services/firebase';
import { HealthRecord } from '../../constants/Types';

export default function TimelineScreen() {
  const [records, setRecords] = useState<HealthRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<HealthRecord | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [filterType, setFilterType] = useState<'all' | 'blood' | 'liver' | 'lipid'>('all');

  useEffect(() => {
    loadHealthRecords();
  }, []);

  const loadHealthRecords = async () => {
    try {
      const user = authService.getCurrentUser();
      if (user) {
        const fetchedRecords = await healthRecordsService.getRecords(user.uid);
        setRecords(fetchedRecords);
      }
    } catch (error) {
      console.error('Error loading health records:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadHealthRecords();
  };

  const openRecordDetail = (record: HealthRecord) => {
    setSelectedRecord(record);
    setModalVisible(true);
  };

  const closeModal = () => {
    setModalVisible(false);
    setSelectedRecord(null);
  };

  const getFilteredRecords = () => {
    if (filterType === 'all') return records;
    
    return records.filter((record) => {
      const type = record.type.toLowerCase();
      switch (filterType) {
        case 'blood':
          return type.includes('blood');
        case 'liver':
          return type.includes('liver');
        case 'lipid':
          return type.includes('lipid');
        default:
          return true;
      }
    });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  const filteredRecords = getFilteredRecords();

  if (loading) {
    return <LoadingOverlay message="Loading timeline..." />;
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Health Timeline</Text>
        <Text style={styles.subtitle}>
          {filteredRecords.length} {filteredRecords.length === 1 ? 'record' : 'records'}
        </Text>
      </View>

      {/* Filter Tabs */}
      <View style={styles.filterContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <TouchableOpacity
            style={[styles.filterTab, filterType === 'all' && styles.filterTabActive]}
            onPress={() => setFilterType('all')}
          >
            <Text style={[styles.filterText, filterType === 'all' && styles.filterTextActive]}>
              All
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.filterTab, filterType === 'blood' && styles.filterTabActive]}
            onPress={() => setFilterType('blood')}
          >
            <Text style={[styles.filterText, filterType === 'blood' && styles.filterTextActive]}>
              Blood Tests
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.filterTab, filterType === 'liver' && styles.filterTabActive]}
            onPress={() => setFilterType('liver')}
          >
            <Text style={[styles.filterText, filterType === 'liver' && styles.filterTextActive]}>
              Liver Function
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.filterTab, filterType === 'lipid' && styles.filterTabActive]}
            onPress={() => setFilterType('lipid')}
          >
            <Text style={[styles.filterText, filterType === 'lipid' && styles.filterTextActive]}>
              Lipid Panel
            </Text>
          </TouchableOpacity>
        </ScrollView>
      </View>

      {/* Timeline */}
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {filteredRecords.length > 0 ? (
          <View style={styles.timeline}>
            {filteredRecords.map((record, index) => (
              <TouchableOpacity
                key={record.id}
                onPress={() => openRecordDetail(record)}
                activeOpacity={0.7}
              >
                <TimelineCard
                  date={record.date}
                  title={record.type}
                  facility={record.facility}
                  isFirst={index === 0}
                  isLast={index === filteredRecords.length - 1}
                />
              </TouchableOpacity>
            ))}
          </View>
        ) : (
          <View style={styles.emptyState}>
            <Ionicons name="calendar-outline" size={64} color="#D1D5DB" />
            <Text style={styles.emptyText}>No records found</Text>
            <Text style={styles.emptySubtext}>
              {filterType === 'all'
                ? 'Start by uploading your first medical document'
                : 'No records match the selected filter'}
            </Text>
          </View>
        )}
      </ScrollView>

      {/* Record Detail Modal */}
      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={closeModal}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {/* Modal Header */}
            <View style={styles.modalHeader}>
              <View style={styles.modalHeaderText}>
                <Text style={styles.modalTitle}>
                  {selectedRecord?.type}
                </Text>
                <Text style={styles.modalSubtitle}>
                  {selectedRecord && formatDate(selectedRecord.date)}
                </Text>
              </View>
              <TouchableOpacity onPress={closeModal} style={styles.closeButton}>
                <Ionicons name="close" size={24} color={Colors.light.text} />
              </TouchableOpacity>
            </View>

            {/* Facility Info */}
            <View style={styles.facilityCard}>
              <Ionicons name="business" size={20} color={Colors.light.primary} />
              <Text style={styles.facilityText}>{selectedRecord?.facility}</Text>
            </View>

            {/* Biomarkers */}
            <ScrollView style={styles.biomarkersScroll}>
              <Text style={styles.sectionTitle}>Test Results</Text>
              {selectedRecord &&
                Object.entries(selectedRecord.biomarkers).map(([key, biomarker]) => (
                  <BiomarkerDisplay key={key} name={key} biomarker={biomarker} />
                ))}

              {/* Original Document */}
              <View style={styles.documentSection}>
                <Text style={styles.sectionTitle}>Original Document</Text>
                <TouchableOpacity style={styles.documentButton}>
                  <Ionicons name="document-text" size={24} color={Colors.light.primary} />
                  <Text style={styles.documentButtonText}>
                    {selectedRecord?.originalDocument || 'View Document'}
                  </Text>
                  <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
                </TouchableOpacity>
              </View>

              {/* Actions */}
              <View style={styles.actionsSection}>
                <TouchableOpacity style={styles.actionButton}>
                  <Ionicons name="share-outline" size={20} color={Colors.light.primary} />
                  <Text style={styles.actionButtonText}>Share Report</Text>
                </TouchableOpacity>
                
                <TouchableOpacity style={styles.actionButton}>
                  <Ionicons name="download-outline" size={20} color={Colors.light.primary} />
                  <Text style={styles.actionButtonText}>Download PDF</Text>
                </TouchableOpacity>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.light.background,
  },
  header: {
    padding: 20,
    paddingTop: 10,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: Colors.light.text,
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  filterContainer: {
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  filterTab: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: Colors.light.cardBackground,
    marginRight: 8,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  filterTabActive: {
    backgroundColor: Colors.light.primary,
    borderColor: Colors.light.primary,
  },
  filterText: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.light.text,
  },
  filterTextActive: {
    color: '#FFFFFF',
  },
  scrollView: {
    flex: 1,
  },
  timeline: {
    padding: 20,
    paddingTop: 0,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 80,
    paddingHorizontal: 32,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: '600',
    color: Colors.light.text,
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 8,
    textAlign: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: Colors.light.background,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    height: '90%',
    paddingTop: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  modalHeaderText: {
    flex: 1,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: Colors.light.text,
  },
  modalSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  closeButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: Colors.light.cardBackground,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  facilityCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.light.cardBackground,
    marginHorizontal: 20,
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  facilityText: {
    fontSize: 16,
    fontWeight: '500',
    color: Colors.light.text,
    marginLeft: 12,
  },
  biomarkersScroll: {
    flex: 1,
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: Colors.light.text,
    marginBottom: 16,
  },
  documentSection: {
    marginTop: 24,
  },
  documentButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.light.cardBackground,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  documentButtonText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '500',
    color: Colors.light.text,
    marginLeft: 12,
  },
  actionsSection: {
    flexDirection: 'row',
    marginTop: 24,
    marginBottom: 32,
    gap: 12,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: Colors.light.cardBackground,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: Colors.light.text,
    marginLeft: 8,
  },
});
