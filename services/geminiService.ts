import { GoogleGenAI } from "@google/genai";
import { SourceChunk, AppSettings, Conversation, ConversationHeader } from '../types';
import { INITIAL_SYSTEM_INSTRUCTION } from '../constants';

const createClient = (apiKey: string) => new GoogleGenAI({ apiKey });

const API_BASE_URL = "http://localhost:5000/api";

export const getConversations = async (): Promise<ConversationHeader[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching conversations:", error);
    throw error;
  }
};

export const getConversation = async (id: string): Promise<Conversation> => {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching conversation ${id}:`, error);
    throw error;
  }
};

export const saveConversation = async (conversation: Conversation): Promise<{success: boolean; id: string}> => {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(conversation),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error saving conversation ${conversation.id}:`, error);
    throw error;
  }
}

export const generateRAGResponse = async (
  query: string,
  chunks: SourceChunk[],
  settings: AppSettings,
  chatHistory: { role: string; parts: { text: string }[] }[] = []
) => {
  if (!settings.apiKey) {
    throw new Error("API Key is missing. Please check settings.");
  }

  const client = createClient(settings.apiKey);
  
  // Rich context formatting for Scriptures
  const contextString = chunks.map(chunk => {
    const loc = chunk.chapter && chunk.verse 
      ? `Chapter ${chunk.chapter}, Verse ${chunk.verse}` 
      : `Page ${chunk.pageNumber}`;
      
    return `
---
ID: ${chunk.id}
SOURCE: ${chunk.bookTitle} (${loc})
TEXT: ${chunk.content}
---
`;
  }).join('\n');

  const finalPrompt = `
RETRIEVED SCRIPTURAL CONTEXT:
${contextString}

USER QUESTION:
${query}

INSTRUCTIONS:
1.  Answer the user's question in detail, based STRICTLY on the "RETRIEVED SCRIPTURAL CONTEXT" provided above. Do not use any other information.
2.  Your answer should be comprehensive and detailed, aiming for 2-3 times longer than a typical brief response.
3.  Synthesize information from multiple context chunks if they are relevant to the user's question.
4.  For every claim or piece of information you use, you MUST cite the source using the format [[ID]], for example: "The soul is described as eternal [[ID:1]] and unchangeable [[ID:2]]".
5.  If the context does not contain the answer, state that clearly.
`;

  try {
    const response = await client.models.generateContent({
      model: settings.model,
      contents: [
        ...chatHistory.map(msg => ({
          role: msg.role,
          parts: msg.parts
        })),
        {
          role: 'user',
          parts: [{ text: finalPrompt }]
        }
      ],
      config: {
        systemInstruction: INITIAL_SYSTEM_INSTRUCTION,
        temperature: 0.3, 
      }
    });

    return response.text || "I could not generate a response.";
  } catch (error) {
    console.error("Gemini API Error:", error);
    throw error;
  }
};
