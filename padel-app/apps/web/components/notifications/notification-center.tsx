"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Bell, BellOff, X, Check, Trash2 } from 'lucide-react';
import { Button } from '@workspace/ui/components/button';
import { Badge } from '@workspace/ui/components/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@workspace/ui/components/card';
import { Popover, PopoverContent, PopoverTrigger } from '@workspace/ui/components/popover';
import { ScrollArea } from '@workspace/ui/components/scroll-area';
import { Separator } from '@workspace/ui/components/separator';
import { toast } from 'sonner';
import { formatDistanceToNow } from 'date-fns';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';

interface Notification {
  id: number;
  type: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  title: string;
  message: string;
  data?: Record<string, unknown>;
  action_url?: string;
  action_text?: string;
  read: boolean;
  read_at?: string;
  created_at: string;
  expires_at?: string;
}

interface NotificationListResponse {
  notifications: Notification[];
  total_unread: number;
  has_more: boolean;
}

const NOTIFICATION_TYPES: Record<string, { icon: string; color: string }> = {
  GAME_STARTING: { icon: '🎾', color: 'bg-blue-500' },
  GAME_ENDED: { icon: '⏰', color: 'bg-green-500' },
  SCORE_SUBMITTED: { icon: '📊', color: 'bg-orange-500' },
  SCORE_CONFIRMED: { icon: '✅', color: 'bg-green-500' },
  SCORE_DISPUTED: { icon: '⚠️', color: 'bg-red-500' },
  TEAM_INVITATION: { icon: '👥', color: 'bg-purple-500' },
  GAME_INVITATION: { icon: '🎮', color: 'bg-blue-500' },
  TOURNAMENT_REMINDER: { icon: '🏆', color: 'bg-yellow-500' },
  ELO_UPDATE: { icon: '📈', color: 'bg-indigo-500' },
  GENERAL: { icon: '📢', color: 'bg-gray-500' },
};

const PRIORITY_COLORS: Record<string, string> = {
  LOW: 'border-l-gray-400',
  MEDIUM: 'border-l-blue-500',
  HIGH: 'border-l-orange-500',
  URGENT: 'border-l-red-500',
};

export function NotificationCenter() {
  const { accessToken } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  const fetchNotifications = useCallback(async (reset: boolean = false) => {
    if (!accessToken) return;
    
    setIsLoading(true);
    try {
      const currentPage = reset ? 1 : page;
      const response = await apiClient.get<NotificationListResponse>(
        `/notifications?skip=${(currentPage - 1) * 20}&limit=20&include_read=true`,
        undefined,
        accessToken
      );
      
      if (reset) {
        setNotifications(response.notifications);
        setPage(1);
      } else {
        setNotifications(prev => [...prev, ...response.notifications]);
      }
      
      setUnreadCount(response.total_unread);
      setHasMore(response.has_more);
      
      if (!reset) setPage(prev => prev + 1);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      toast.error('Failed to load notifications');
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, page]);

  const fetchUnreadCount = useCallback(async () => {
    if (!accessToken) return;
    
    try {
      const response = await apiClient.get<{ unread_count: number }>('/notifications/unread-count', undefined, accessToken);
      setUnreadCount(response.unread_count);
    } catch (error) {
      console.error('Error fetching unread count:', error);
    }
  }, [accessToken]);

  const markAsRead = async (notificationId: number) => {
    if (!accessToken) return;
    
    try {
      await apiClient.post(`/notifications/${notificationId}/mark-read`, {}, { token: accessToken });
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, read: true, read_at: new Date().toISOString() } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
      toast.error('Failed to mark notification as read');
    }
  };

  const markAllAsRead = async () => {
    if (!accessToken) return;
    
    try {
      await apiClient.post('/notifications/mark-all-read', {}, { token: accessToken });
      setNotifications(prev => 
        prev.map(n => ({ ...n, read: true, read_at: new Date().toISOString() }))
      );
      setUnreadCount(0);
      toast.success('All notifications marked as read');
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      toast.error('Failed to mark all notifications as read');
    }
  };

  const deleteNotification = async (notificationId: number) => {
    if (!accessToken) return;
    
    try {
      await apiClient.delete(`/notifications/${notificationId}`, accessToken);
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
      // Update unread count if the deleted notification was unread
      const deletedNotification = notifications.find(n => n.id === notificationId);
      if (deletedNotification && !deletedNotification.read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      toast.success('Notification deleted');
    } catch (error) {
      console.error('Error deleting notification:', error);
      toast.error('Failed to delete notification');
    }
  };

  const handleNotificationAction = (notification: Notification) => {
    if (notification.action_url) {
      window.location.href = notification.action_url;
    }
    if (!notification.read) {
      markAsRead(notification.id);
    }
  };

  useEffect(() => {
    if (isOpen && accessToken) {
      fetchNotifications(true);
    }
  }, [isOpen, accessToken, fetchNotifications]);

  useEffect(() => {
    if (accessToken) {
      fetchUnreadCount();
      // Poll for new notifications every 30 seconds
      const interval = setInterval(fetchUnreadCount, 30000);
      return () => clearInterval(interval);
    }
  }, [accessToken, fetchUnreadCount]);

  const NotificationItem = ({ notification }: { notification: Notification }) => {
    const typeInfo = NOTIFICATION_TYPES[notification.type] || NOTIFICATION_TYPES.GENERAL!;
    const priorityColor = PRIORITY_COLORS[notification.priority] || PRIORITY_COLORS.MEDIUM!
    
    return (
      <Card 
        className={`mb-2 cursor-pointer transition-all border-l-4 ${priorityColor} ${
          !notification.read ? 'bg-blue-50 dark:bg-blue-900/10' : ''
        }`}
        onClick={() => handleNotificationAction(notification)}
      >
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              <div className={`w-2 h-2 rounded-full mt-2 ${typeInfo.color}`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-lg">{typeInfo.icon}</span>
                  <h4 className="font-semibold text-sm truncate">{notification.title}</h4>
                  {!notification.read && (
                    <Badge variant="secondary" className="text-xs">New</Badge>
                  )}
                </div>
                <p className="text-sm text-muted-foreground mb-2">{notification.message}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                  </span>
                  {notification.action_text && (
                    <span className="text-xs text-primary font-medium">{notification.action_text}</span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-1 ml-2">
              {!notification.read && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    markAsRead(notification.id);
                  }}
                >
                  <Check className="h-4 w-4" />
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  deleteNotification(notification.id);
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="sm" className="relative">
          {unreadCount > 0 ? <Bell className="h-5 w-5" /> : <BellOff className="h-5 w-5" />}
          {unreadCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-96 p-0" align="end">
        <Card className="border-0 shadow-lg">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Notifications</CardTitle>
              <div className="flex items-center space-x-2">
                {unreadCount > 0 && (
                  <Button variant="ghost" size="sm" onClick={markAllAsRead}>
                    <Check className="h-4 w-4 mr-1" />
                    Mark all read
                  </Button>
                )}
                <Button variant="ghost" size="sm" onClick={() => setIsOpen(false)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
            {unreadCount > 0 && (
              <p className="text-sm text-muted-foreground">
                You have {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
              </p>
            )}
          </CardHeader>
          <Separator />
          <ScrollArea className="h-96">
            <div className="p-4">
              {notifications.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Bell className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No notifications yet</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {notifications.map((notification) => (
                    <NotificationItem key={notification.id} notification={notification} />
                  ))}
                  {hasMore && (
                    <Button 
                      variant="outline" 
                      className="w-full mt-4" 
                      onClick={() => fetchNotifications(false)}
                      disabled={isLoading}
                    >
                      {isLoading ? 'Loading...' : 'Load More'}
                    </Button>
                  )}
                </div>
              )}
            </div>
          </ScrollArea>
        </Card>
      </PopoverContent>
    </Popover>
  );
}