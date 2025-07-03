# Text-Compression-Algorithm

### Traditional text compression algorithms compress using syntactic patterns or common word/phrase simplifications. My approach is to store a sentence in a simplified form that stores only important words while also tracking several parameters about the sentence that can help reconstruct a similar sentence.
### Each sentence has a weight for formality and tone are calculated for each parameter based on each of the encountered words for each category. So if a formal word is encountered, our formal weight is incremented by 1, and if an informal word is encountered, then we decrement. This pattern is repeated for each parameter. Core subjects and words are also stored, and all of these are used in the reconstruction with Gemini.
