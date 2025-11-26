 
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Colors from '../constants/Colors';

interface TimelineCardProps {
  date: string;
  title: string;
  facility: string;
  isFirst?: boolean;
  isLast?: boolean;
}

export default function TimelineCard({ date, title, facility, isFirst, isLast }: TimelineCardProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return {
      day: date.getDate(),
      month: date.toLocaleDateString('en-IN', { month: 'short' }),
      year: date.getFullYear(),
    };
  };

  const formattedDate = formatDate(date);

  return (
    <View style={styles.container}>
      <View style={styles.timeline}>
        <View style={[styles.dot, isFirst && styles.dotFirst]} />
        {!isLast && <View style={styles.line} />}
      </View>
      
      <View style={styles.content}>
        <View style={styles.dateContainer}>
          <Text style={styles.day}>{formattedDate.day}</Text>
          <Text style={styles.month}>{formattedDate.month}</Text>
          <Text style={styles.year}>{formattedDate.year}</Text>
        </View>
        
        <View style={styles.card}>
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.facility}>{facility}</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  timeline: {
    width: 40,
    alignItems: 'center',
  },
  dot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: Colors.light.primary,
    borderWidth: 3,
    borderColor: Colors.light.background,
    zIndex: 1,
  },
  dotFirst: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: Colors.light.accent,
  },
  line: {
    flex: 1,
    width: 2,
    backgroundColor: Colors.light.border,
    marginTop: -6,
  },
  content: {
    flex: 1,
    flexDirection: 'row',
  },
  dateContainer: {
    width: 60,
    alignItems: 'center',
    marginRight: 12,
  },
  day: {
    fontSize: 24,
    fontWeight: '700',
    color: Colors.light.text,
  },
  month: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6B7280',
    textTransform: 'uppercase',
  },
  year: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  card: {
    flex: 1,
    backgroundColor: Colors.light.cardBackground,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: Colors.light.border,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: Colors.light.text,
    marginBottom: 4,
  },
  facility: {
    fontSize: 14,
    color: '#6B7280',
  },
});
