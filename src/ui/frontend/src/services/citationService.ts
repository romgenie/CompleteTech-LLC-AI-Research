import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { CitationManager, CitationPaper, CitationStyle } from '../utils/citationManager';
import { ApiResponse } from '../types';

/**
 * Interface for DOI lookup response
 */
interface DOIResponse {
  title: string;
  authors: Array<{
    given: string;
    family: string;
    sequence: string;
  }>;
  abstract?: string;
  published?: {
    'date-parts': number[][];
  };
  'container-title'?: string;
  volume?: string;
  issue?: string;
  page?: string;
  publisher?: string;
  DOI?: string;
  URL?: string;
}

/**
 * Interface for ArXiv API response
 */
interface ArXivResponse {
  feed: {
    entry: Array<{
      title: string;
      author: Array<{
        name: string;
      }>;
      summary: string;
      published: string;
      'arxiv:journal_ref'?: string;
      'arxiv:doi'?: string;
      link: Array<{
        href: string;
        rel: string;
        type?: string;
      }>;
      id: string;
    }>;
  };
}

// Create axios instance for citation services
const citationApi: AxiosInstance = axios.create({
  baseURL: '/citations',
});

// Add request interceptor to add authentication token
citationApi.interceptors.request.use(
  (config: AxiosRequestConfig): AxiosRequestConfig => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }
);

// Crossref API for DOI lookups
const crossrefApi = axios.create({
  baseURL: 'https://api.crossref.org/works',
});

// ArXiv API for ArXiv ID lookups
const arxivApi = axios.create({
  baseURL: 'http://export.arxiv.org/api/query',
});

/**
 * Service for managing citations and related operations
 */
const citationService = {
  // Create a new citation manager instance
  manager: new CitationManager(),

  /**
   * Add a paper to the citation manager
   * 
   * @param paper - Paper to add
   */
  addPaper(paper: CitationPaper): void {
    this.manager.addPaper(paper);
  },

  /**
   * Add multiple papers to the citation manager
   * 
   * @param papers - Papers to add
   */
  addPapers(papers: CitationPaper[]): void {
    papers.forEach(paper => this.manager.addPaper(paper));
  },

  /**
   * Get all papers in the citation manager
   * 
   * @returns Array of papers
   */
  getAllPapers(): CitationPaper[] {
    return this.manager.getAllPapers();
  },

  /**
   * Get a formatted citation for a paper
   * 
   * @param paper - Paper to cite
   * @param style - Citation style
   * @returns Formatted citation string
   */
  formatCitation(paper: CitationPaper, style: CitationStyle = 'APA'): string {
    return this.manager.cite(paper, style);
  },

  /**
   * Format a bibliography of all papers in the citation manager
   * 
   * @param style - Citation style
   * @returns Formatted bibliography string
   */
  formatBibliography(style: CitationStyle = 'APA'): string {
    const papers = this.manager.getAllPapers();
    return this.manager.formatReferences(papers, style);
  },

  /**
   * Export a bibliography of all papers in BibTeX format
   * 
   * @returns BibTeX string
   */
  exportBibTeX(): string {
    const papers = this.manager.getAllPapers();
    return this.manager.exportBibTeX(papers);
  },

  /**
   * Export a bibliography in a specified format
   * 
   * @param style - Citation style
   * @param format - Export format (txt, html, bibtex)
   * @returns Formatted bibliography string
   */
  exportBibliography(style: CitationStyle = 'APA', format: 'txt' | 'html' | 'bibtex' = 'txt'): string {
    const papers = this.manager.getAllPapers();
    
    if (format === 'bibtex' || style === 'BibTeX') {
      return this.manager.exportBibTeX(papers);
    }
    
    const citations = papers.map((paper, index) => {
      const citation = this.manager.cite(paper, style);
      return format === 'html' 
        ? `<p id="citation-${index+1}">[${index+1}] ${citation}</p>` 
        : `[${index+1}] ${citation}`;
    });
    
    return format === 'html'
      ? `<div class="bibliography">\n${citations.join('\n')}\n</div>`
      : citations.join('\n\n');
  },

  /**
   * Look up paper metadata by DOI using CrossRef API
   * 
   * @param doi - DOI to look up
   * @returns Paper metadata
   */
  async lookupDOI(doi: string): Promise<CitationPaper> {
    try {
      // Try server-side lookup first (preferred for production)
      try {
        const response = await citationApi.get<ApiResponse<CitationPaper>>(`/lookup/doi/${doi}`);
        return response.data.data as CitationPaper;
      } catch (serverError) {
        console.warn('Server-side DOI lookup failed, falling back to direct API call:', serverError);
        
        // Fall back to direct API call
        const response = await crossrefApi.get<{message: DOIResponse}>(`/${doi}`);
        const data = response.data.message;
        
        // Format authors from Crossref format to simple strings
        const authors = data.authors?.map(author => 
          `${author.given || ''} ${author.family || ''}`.trim()
        ) || [];
        
        // Extract year from published date
        let year: string | undefined;
        if (data.published && data.published['date-parts'] && data.published['date-parts'][0]) {
          year = data.published['date-parts'][0][0]?.toString();
        }
        
        // Create CitationPaper object
        const paper: CitationPaper = {
          id: doi,
          title: data.title || '',
          authors,
          year,
          journal: data['container-title']?.[0],
          volume: data.volume,
          issue: data.issue,
          pages: data.page,
          publisher: data.publisher,
          url: data.URL,
          doi,
          abstract: data.abstract
        };
        
        // Add to citation manager
        this.addPaper(paper);
        
        return paper;
      }
    } catch (error) {
      console.error('Error looking up DOI:', error);
      throw new Error(`Failed to look up DOI: ${doi}`);
    }
  },

  /**
   * Look up paper metadata by ArXiv ID
   * 
   * @param arxivId - ArXiv ID to look up
   * @returns Paper metadata
   */
  async lookupArXiv(arxivId: string): Promise<CitationPaper> {
    try {
      // Try server-side lookup first (preferred for production)
      try {
        const response = await citationApi.get<ApiResponse<CitationPaper>>(`/lookup/arxiv/${arxivId}`);
        return response.data.data as CitationPaper;
      } catch (serverError) {
        console.warn('Server-side ArXiv lookup failed, falling back to direct API call:', serverError);
        
        // Fall back to direct API call
        const response = await arxivApi.get<ArXivResponse>(`?id_list=${arxivId}`);
        const entry = response.data.feed.entry[0];
        
        if (!entry) {
          throw new Error(`No results found for ArXiv ID: ${arxivId}`);
        }
        
        // Format authors
        const authors = entry.author.map(author => author.name);
        
        // Extract year from published date
        const year = new Date(entry.published).getFullYear().toString();
        
        // Get URL
        const url = entry.link.find(link => link.rel === 'alternate')?.href || '';
        
        // Create CitationPaper object
        const paper: CitationPaper = {
          id: arxivId,
          title: entry.title || '',
          authors,
          year,
          journal: entry['arxiv:journal_ref'] || 'arXiv',
          doi: entry['arxiv:doi'],
          url,
          arxivId,
          abstract: entry.summary
        };
        
        // Add to citation manager
        this.addPaper(paper);
        
        return paper;
      }
    } catch (error) {
      console.error('Error looking up ArXiv ID:', error);
      throw new Error(`Failed to look up ArXiv ID: ${arxivId}`);
    }
  },

  /**
   * Lookup a paper by URL (try to determine if it's DOI, ArXiv, etc.)
   * 
   * @param url - URL to lookup
   * @returns Paper metadata
   */
  async lookupUrl(url: string): Promise<CitationPaper> {
    // Check if URL is a DOI
    const doiMatch = url.match(/10\.\d{4,}\/[-._;()/:A-Za-z0-9]+/);
    if (doiMatch) {
      return this.lookupDOI(doiMatch[0]);
    }
    
    // Check if URL is an ArXiv URL
    const arxivMatch = url.match(/arxiv\.org\/abs\/(\d+\.\d+)/);
    if (arxivMatch) {
      return this.lookupArXiv(arxivMatch[1]);
    }
    
    // If all else fails, create a minimal citation with just the URL
    const paper: CitationPaper = {
      id: `url-${Date.now()}`,
      title: 'Unknown Publication',
      authors: ['Unknown Author'],
      url
    };
    
    this.addPaper(paper);
    return paper;
  },

  /**
   * Save user citation preferences
   * 
   * @param preferences - User preferences for citations
   * @returns Success status
   */
  async savePreferences(preferences: {
    defaultStyle: CitationStyle;
    includeAbstract: boolean;
    defaultFormat: 'txt' | 'html' | 'bibtex';
  }): Promise<boolean> {
    try {
      await citationApi.post('/preferences', preferences);
      // Also save to localStorage as a fallback
      localStorage.setItem('citationPreferences', JSON.stringify(preferences));
      return true;
    } catch (error) {
      console.error('Error saving citation preferences:', error);
      // Still save to localStorage even if API call fails
      localStorage.setItem('citationPreferences', JSON.stringify(preferences));
      return false;
    }
  },

  /**
   * Get user citation preferences
   * 
   * @returns User preferences for citations
   */
  async getPreferences(): Promise<{
    defaultStyle: CitationStyle;
    includeAbstract: boolean;
    defaultFormat: 'txt' | 'html' | 'bibtex';
  }> {
    try {
      const response = await citationApi.get('/preferences');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching citation preferences:', error);
      // Fall back to localStorage
      const savedPreferences = localStorage.getItem('citationPreferences');
      if (savedPreferences) {
        return JSON.parse(savedPreferences);
      }
      // Return defaults if no saved preferences
      return {
        defaultStyle: 'APA',
        includeAbstract: false,
        defaultFormat: 'txt'
      };
    }
  },

  /**
   * Get a list of all supported citation styles
   * 
   * @returns Array of supported citation styles
   */
  getSupportedStyles(): CitationStyle[] {
    return ['APA', 'MLA', 'Chicago', 'IEEE', 'Harvard', 'Vancouver', 'BibTeX'];
  },

  /**
   * Create a citation manager from research results
   * 
   * @param results - Array of research results
   * @returns New citation manager with the results
   */
  createManagerFromResults(results: any[]): CitationManager {
    const manager = new CitationManager();
    
    results.forEach(result => {
      const paper = CitationManager.fromResearchResult(result);
      manager.addPaper(paper);
    });
    
    return manager;
  }
};

export default citationService;