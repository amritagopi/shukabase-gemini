import React from 'react';
import { ConversationHeader } from './types';

interface ConversationHistoryProps {
  conversations: ConversationHeader[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
}

const ConversationHistory: React.FC<ConversationHistoryProps> = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
}) => {
  return (
    <div className="w-64 bg-slate-800 p-4 flex flex-col h-full">
      <button 
        onClick={onNewChat} 
        className="w-full bg-indigo-500 hover:bg-indigo-600 text-white font-bold py-2 px-4 rounded-lg mb-4 transition-colors duration-200"
      >
        + New Chat
      </button>
      <div className="flex-grow overflow-y-auto">
        <ul>
          {conversations.map((convo) => (
            <li
              key={convo.id}
              className={`p-3 rounded-lg cursor-pointer mb-2 transition-colors duration-150 ${
                convo.id === activeConversationId 
                  ? 'bg-slate-700' 
                  : 'hover:bg-slate-700/50'
              }`}
              onClick={() => onSelectConversation(convo.id)}
            >
              <div className="font-semibold text-slate-100 truncate">{convo.title}</div>
              <div className="text-xs text-slate-400 mt-1">
                {new Date(convo.createdAt).toLocaleString()}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ConversationHistory;
