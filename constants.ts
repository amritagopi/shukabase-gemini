import { SourceChunk } from './types';

// Demo data simulating the Shukabase structure
export const DEMO_CHUNKS: SourceChunk[] = [
  {
    id: "bg.2.13",
    bookTitle: "Bhagavad Gita",
    chapter: 2,
    verse: 13,
    score: 0.95,
    content: "As the embodied soul continuously passes, in this body, from boyhood to youth to old age, the soul similarly passes into another body at death. A sober person is not bewildered by such a change."
  },
  {
    id: "bg.2.20",
    bookTitle: "Bhagavad Gita",
    chapter: 2,
    verse: 20,
    score: 0.89,
    content: "For the soul there is neither birth nor death at any time. He has not come into being, does not come into being, and will not come into being. He is unborn, eternal, ever-existing and primeval. He is not slain when the body is slain."
  },
  {
    id: "bg.4.7",
    bookTitle: "Bhagavad Gita",
    chapter: 4,
    verse: 7,
    score: 0.82,
    content: "Whenever and wherever there is a decline in religious practice, O descendant of Bharata, and a predominant rise of irreligion—at that time I descend Myself."
  },
  {
    id: "sb.1.1.1",
    bookTitle: "Srimad Bhagavatam",
    chapter: 1,
    verse: 1,
    score: 0.75,
    content: "O my Lord, Sri Krishna, son of Vasudeva, O all-pervading Personality of Godhead, I offer my respectful obeisances unto You. I meditate upon Lord Sri Krishna because He is the Absolute Truth and the primeval cause of all causes of the creation, sustenance and destruction of the manifested universes."
  }
];

export const INITIAL_SYSTEM_INSTRUCTION = `
You are an expert assistant for Vaishnava Scriptures (Shukabase).
You have access to retrieved verses from books like Bhagavad Gita, Srimad Bhagavatam, etc.

CRITICAL INSTRUCTIONS:
1. Answer the user's question using ONLY the provided context chunks.
2. CITATIONS ARE MANDATORY. When using information from a verse, append its ID like this: [[id]].
   Example: "The soul passes to another body at death [[bg.2.13]]."
3. If the context does not contain the answer, humbly state that it is not in the current retrieved verses.
4. Be respectful and philosophical in tone.
5. Answer in the same language as the user's question (Russian or English).
`;