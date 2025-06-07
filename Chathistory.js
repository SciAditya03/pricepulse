'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MessageCircle, Clock, Search, Trash2, MoreVertical } from 'lucide-react';

const ChatHistory = ({ onChatSelect, currentChatId }) => {
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedChat, setSelectedChat] = useState(null);
  const router = useRouter();

  // Fetch chat history using Next.js API routes
  const fetchChatHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/chats', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setChatHistory(data.chats || []);
    } catch (error) {
      console.error('Error fetching chat history:', error);
      // Handle error - you can add toast notification here
    } finally {
      setLoading(false);
    }
  };

  // Fetch specific chat details when clicked
  const handleChatClick = async (chatId) => {
    try {
      setSelectedChat(chatId);
      
      const response = await fetch(`/api/chats/${chatId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const chatData = await response.json();
      
      // Pass the chat data to parent component
      onChatSelect(chatData);
      
      // Optional: Update URL without page refresh
      router.push(`/chat/${chatId}`, { shallow: true });
      
    } catch (error) {
      console.error('Error fetching chat details:', error);
      // Handle error
    }
  };

  // Delete chat
  const handleDeleteChat = async (chatId, e) => {
    e.stopPropagation(); // Prevent chat selection when deleting
    
    if (!window.confirm('Are you sure you want to delete this chat?')) {
      return;
    }

    try {
      const response = await fetch(`/api/chats/${chatId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Remove from local state
      setChatHistory(prev => prev.filter(chat => chat.id !== chatId));
      
      // If deleted chat was currently selected, redirect to home
      if (currentChatId === chatId) {
        router.push('/chat');
      }
      
    } catch (error) {
      console.error('Error deleting chat:', error);
    }
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  // Filter chats based on search
  const filteredChats = chatHistory.filter(chat =>
    chat.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    chat.preview.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Group chats by date
  const groupedChats = filteredChats.reduce((groups, chat) => {
    const date = formatDate(chat.updatedAt);
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(chat);
    return groups;
  }, {});

  useEffect(() => {
    fetchChatHistory();
  }, []);

  // Loading skeleton
  if (loading) {
    return (
      <div className="w-80 bg-gray-50 border-r border-gray-200 p-4">
        <div className="animate-pulse">
          <div className="h-10 bg-gray-200 rounded mb-4"></div>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 rounded mb-2"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Chat History</h2>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search chats..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto">
        {Object.keys(groupedChats).length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <MessageCircle className="w-12 h-12 mx-auto text-gray-300 mb-3" />
            <p>No chats found</p>
          </div>
        ) : (
          Object.entries(groupedChats).map(([date, chats]) => (
            <div key={date} className="mb-4">
              {/* Date Header */}
              <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
                {date}
              </div>
              
              {/* Chats for this date */}
              {chats.map((chat) => (
                <div
                  key={chat.id}
                  onClick={() => handleChatClick(chat.id)}
                  className={`mx-2 mb-1 p-3 rounded-lg cursor-pointer transition-colors group hover:bg-white ${
                    currentChatId === chat.id ? 'bg-white shadow-sm border border-blue-200' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-gray-800 truncate">
                        {chat.title}
                      </h3>
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                        {chat.preview}
                      </p>
                      <div className="flex items-center mt-2 text-xs text-gray-400">
                        <Clock className="w-3 h-3 mr-1" />
                        {new Date(chat.updatedAt).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </div>
                    </div>
                    
                    {/* Actions */}
                    <div className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => handleDeleteChat(chat.id, e)}
                        className="p-1 text-gray-400 hover:text-red-500 rounded"
                        title="Delete chat"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 text-xs text-gray-500 text-center">
        {filteredChats.length} chat{filteredChats.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
};

// Next.js Page Component Example
const ChatPage = ({ params }) => {
  const [currentChat, setCurrentChat] = useState(null);
  const [currentChatId, setCurrentChatId] = useState(params?.chatId || null);

  const handleChatSelect = (chatData) => {
    setCurrentChat(chatData);
    setCurrentChatId(chatData.id);
    console.log('Selected chat:', chatData);
  };

  return (
    <div className="flex h-screen">
      <ChatHistory 
        onChatSelect={handleChatSelect}
        currentChatId={currentChatId}
      />
      
      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col">
        {currentChat ? (
          <div className="p-4">
            <h2 className="text-xl font-bold mb-4">{currentChat.title}</h2>
            
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {currentChat.messages?.map((message, index) => (
                <div key={index} className={`p-3 rounded-lg ${
                  message.role === 'user' ? 'bg-blue-100 ml-8' : 'bg-gray-100 mr-8'
                }`}>
                  <div className="text-sm text-gray-600 mb-1">
                    {message.role === 'user' ? 'You' : 'Assistant'}
                  </div>
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>

            {/* Input Area */}
            <div className="border-t pt-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Type your message..."
                  className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                  Send
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <MessageCircle className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium mb-2">Welcome to Chat</h3>
              <p>Select a chat from the history or start a new conversation</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPage;
