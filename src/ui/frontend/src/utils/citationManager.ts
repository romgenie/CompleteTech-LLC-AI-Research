import { Paper } from '../types';

/**
 * Citation styles supported by the citation manager
 */
export type CitationStyle = 'APA' | 'MLA' | 'Chicago' | 'IEEE' | 'Harvard' | 'Vancouver' | 'BibTeX';

/**
 * Interface representing a research paper for citation purposes
 */
export interface CitationPaper {
  id: string;
  title: string;
  authors: string[];  // Array of author names
  year?: string | number;
  journal?: string;
  conference?: string;
  volume?: string | number;
  issue?: string | number;
  pages?: string;
  publisher?: string;
  url?: string;
  doi?: string;
  arxivId?: string;
  abstract?: string;
}

/**
 * Interface for BibTeX fields
 */
export interface BibTeXEntry {
  type: 'article' | 'inproceedings' | 'book' | 'techreport' | 'misc';
  id: string;
  fields: {
    title: string;
    author: string;
    year?: string;
    journal?: string;
    booktitle?: string;
    volume?: string;
    number?: string;
    pages?: string;
    publisher?: string;
    url?: string;
    doi?: string;
    note?: string;
    [key: string]: string | undefined;
  };
}

/**
 * Class for managing citations in various formats
 */
export class CitationManager {
  private papers: CitationPaper[] = [];

  /**
   * Add a paper to the citation manager
   * 
   * @param paper - Paper to add
   */
  public addPaper(paper: CitationPaper): void {
    if (!this.papers.some(p => p.id === paper.id)) {
      this.papers.push(paper);
    }
  }

  /**
   * Get all papers in the citation manager
   * 
   * @returns Array of papers
   */
  public getAllPapers(): CitationPaper[] {
    return [...this.papers];
  }

  /**
   * Get a paper by ID
   * 
   * @param id - Paper ID
   * @returns Paper with the given ID, or undefined if not found
   */
  public getPaper(id: string): CitationPaper | undefined {
    return this.papers.find(p => p.id === id);
  }

  /**
   * Remove a paper from the citation manager
   * 
   * @param id - ID of the paper to remove
   * @returns True if a paper was removed, false otherwise
   */
  public removePaper(id: string): boolean {
    const initialLength = this.papers.length;
    this.papers = this.papers.filter(p => p.id !== id);
    return this.papers.length < initialLength;
  }

  /**
   * Format authors according to the given citation style
   * 
   * @param authors - Array of author names
   * @param style - Citation style
   * @returns Formatted author string
   */
  private formatAuthors(authors: string[], style: CitationStyle): string {
    if (!authors || authors.length === 0) {
      return '';
    }

    // Format authors according to style
    switch (style) {
      case 'APA':
        // APA: Last, F., Last, F., & Last, F.
        return this.formatAuthorsAPA(authors);
      
      case 'MLA':
        // MLA: Last, First, First Last, and First Last.
        return this.formatAuthorsMLA(authors);
      
      case 'Chicago':
        // Chicago: Last, First, First Last, and First Last.
        return this.formatAuthorsChicago(authors);
      
      case 'IEEE':
        // IEEE: F. Last, F. Last, and F. Last
        return this.formatAuthorsIEEE(authors);
      
      case 'Harvard':
        // Harvard: Last, F., Last, F. and Last, F.
        return this.formatAuthorsHarvard(authors);
      
      case 'Vancouver':
        // Vancouver: Last F, Last F, Last F.
        return this.formatAuthorsVancouver(authors);
      
      case 'BibTeX':
        // BibTeX: Last, First and Last, First and Last, First
        return this.formatAuthorsBibTeX(authors);
      
      default:
        return authors.join(', ');
    }
  }

  /**
   * Format authors according to APA style
   * 
   * @param authors - Array of author names
   * @returns Formatted author string in APA style
   */
  private formatAuthorsAPA(authors: string[]): string {
    return authors.map((author, index) => {
      // Split the author name into parts
      const parts = author.split(' ');
      const lastName = parts.pop() || '';
      const firstNameInitials = parts.map(name => name[0] + '.').join(' ');
      
      return `${lastName}, ${firstNameInitials}`;
    }).join(', ');
  }

  /**
   * Format authors according to MLA style
   * 
   * @param authors - Array of author names
   * @returns Formatted author string in MLA style
   */
  private formatAuthorsMLA(authors: string[]): string {
    if (authors.length === 1) {
      // Split the author name into parts
      const parts = authors[0].split(' ');
      const lastName = parts.pop() || '';
      const firstName = parts.join(' ');
      
      return `${lastName}, ${firstName}`;
    } else if (authors.length === 2) {
      // Split the first author name
      const parts1 = authors[0].split(' ');
      const lastName1 = parts1.pop() || '';
      const firstName1 = parts1.join(' ');
      
      return `${lastName1}, ${firstName1}, and ${authors[1]}`;
    } else if (authors.length > 2) {
      // Split the first author name
      const parts1 = authors[0].split(' ');
      const lastName1 = parts1.pop() || '';
      const firstName1 = parts1.join(' ');
      
      return `${lastName1}, ${firstName1}, et al.`;
    }
    
    return '';
  }

  /**
   * Format authors according to Chicago style
   * 
   * @param authors - Array of author names
   * @returns Formatted author string in Chicago style
   */
  private formatAuthorsChicago(authors: string[]): string {
    if (authors.length === 1) {
      // Split the author name into parts
      const parts = authors[0].split(' ');
      const lastName = parts.pop() || '';
      const firstName = parts.join(' ');
      
      return `${lastName}, ${firstName}`;
    } else if (authors.length > 1) {
      // First author: Last, First
      const parts1 = authors[0].split(' ');
      const lastName1 = parts1.pop() || '';
      const firstName1 = parts1.join(' ');
      
      // Subsequent authors: First Last
      const otherAuthors = authors.slice(1);
      
      // Format differently based on number of authors
      if (authors.length <= 3) {
        return `${lastName1}, ${firstName1}, ${otherAuthors.join(', ')}`;
      } else {
        return `${lastName1}, ${firstName1}, et al.`;
      }
    }
    
    return '';
  }

  /**
   * Format authors according to IEEE style
   * 
   * @param authors - Array of author names
   * @returns Formatted author string in IEEE style
   */
  private formatAuthorsIEEE(authors: string[]): string {
    return authors.map((author) => {
      // Split the author name into parts
      const parts = author.split(' ');
      const lastName = parts.pop() || '';
      const initials = parts.map(name => name[0] + '.').join('. ');
      
      return `${initials} ${lastName}`;
    }).join(', ');
  }

  /**
   * Format authors according to Harvard style
   * 
   * @param authors - Array of author names
   * @returns Formatted author string in Harvard style
   */
  private formatAuthorsHarvard(authors: string[]): string {
    if (authors.length <= 3) {
      return authors.map((author) => {
        // Split the author name into parts
        const parts = author.split(' ');
        const lastName = parts.pop() || '';
        const initials = parts.map(name => name[0] + '.').join('');
        
        return `${lastName}, ${initials}`;
      }).join(', ');
    } else {
      // First 3 authors followed by et al.
      const firstThree = authors.slice(0, 3).map((author) => {
        const parts = author.split(' ');
        const lastName = parts.pop() || '';
        const initials = parts.map(name => name[0] + '.').join('');
        
        return `${lastName}, ${initials}`;
      }).join(', ');
      
      return `${firstThree}, et al.`;
    }
  }

  /**
   * Format authors according to Vancouver style
   * 
   * @param authors - Array of author names
   * @returns Formatted author string in Vancouver style
   */
  private formatAuthorsVancouver(authors: string[]): string {
    if (authors.length <= 6) {
      return authors.map((author) => {
        // Split the author name into parts
        const parts = author.split(' ');
        const lastName = parts.pop() || '';
        const initials = parts.map(name => name[0]).join('');
        
        return `${lastName} ${initials}`;
      }).join(', ');
    } else {
      // First 6 authors followed by et al.
      const firstSix = authors.slice(0, 6).map((author) => {
        const parts = author.split(' ');
        const lastName = parts.pop() || '';
        const initials = parts.map(name => name[0]).join('');
        
        return `${lastName} ${initials}`;
      }).join(', ');
      
      return `${firstSix}, et al.`;
    }
  }

  /**
   * Format authors according to BibTeX style
   * 
   * @param authors - Array of author names
   * @returns Formatted author string in BibTeX style
   */
  private formatAuthorsBibTeX(authors: string[]): string {
    return authors.map((author) => {
      // Split the author name into parts
      const parts = author.split(' ');
      const lastName = parts.pop() || '';
      const firstName = parts.join(' ');
      
      return `${lastName}, ${firstName}`;
    }).join(' and ');
  }

  /**
   * Format a paper citation in the given style
   * 
   * @param paper - Paper to cite
   * @param style - Citation style
   * @returns Formatted citation string
   */
  public cite(paper: CitationPaper, style: CitationStyle): string {
    switch (style) {
      case 'APA':
        return this.formatAPA(paper);
      case 'MLA':
        return this.formatMLA(paper);
      case 'Chicago':
        return this.formatChicago(paper);
      case 'IEEE':
        return this.formatIEEE(paper);
      case 'Harvard':
        return this.formatHarvard(paper);
      case 'Vancouver':
        return this.formatVancouver(paper);
      case 'BibTeX':
        return this.formatBibTeX(paper);
      default:
        return this.formatAPA(paper);
    }
  }

  /**
   * Format a paper citation in APA style
   * 
   * @param paper - Paper to cite
   * @returns APA citation string
   */
  public formatAPA(paper: CitationPaper): string {
    const authors = this.formatAuthors(paper.authors, 'APA');
    const year = paper.year ? `(${paper.year})` : '';
    const title = paper.title ? `${paper.title}.` : '';
    
    let publication = '';
    if (paper.journal) {
      // Journal article
      publication = `${paper.journal}`;
      if (paper.volume) {
        publication += `, ${paper.volume}`;
        if (paper.issue) {
          publication += `(${paper.issue})`;
        }
      }
      if (paper.pages) {
        publication += `, ${paper.pages}`;
      }
      publication += '.';
    } else if (paper.conference) {
      // Conference paper
      publication = `In ${paper.conference}`;
      if (paper.pages) {
        publication += ` (pp. ${paper.pages})`;
      }
      if (paper.publisher) {
        publication += `. ${paper.publisher}`;
      }
      publication += '.';
    } else if (paper.publisher) {
      // Book or report
      publication = `${paper.publisher}.`;
    }
    
    const doi = paper.doi ? `https://doi.org/${paper.doi}` : '';
    
    return `${authors} ${year}. ${title} ${publication} ${doi}`.trim().replace(/\s+/g, ' ');
  }

  /**
   * Format a paper citation in MLA style
   * 
   * @param paper - Paper to cite
   * @returns MLA citation string
   */
  public formatMLA(paper: CitationPaper): string {
    const authors = this.formatAuthors(paper.authors, 'MLA');
    const title = `"${paper.title}."`;
    
    let publication = '';
    if (paper.journal) {
      // Journal article
      publication = `${paper.journal}`;
      if (paper.volume) {
        publication += `, vol. ${paper.volume}`;
        if (paper.issue) {
          publication += `, no. ${paper.issue}`;
        }
      }
      if (paper.year) {
        publication += `, ${paper.year}`;
      }
      if (paper.pages) {
        publication += `, pp. ${paper.pages}`;
      }
    } else if (paper.conference) {
      // Conference paper
      publication = `${paper.conference}`;
      if (paper.year) {
        publication += `, ${paper.year}`;
      }
      if (paper.pages) {
        publication += `, pp. ${paper.pages}`;
      }
      if (paper.publisher) {
        publication += `, ${paper.publisher}`;
      }
    } else if (paper.publisher) {
      // Book or report
      publication = `${paper.publisher}`;
      if (paper.year) {
        publication += `, ${paper.year}`;
      }
    } else if (paper.year) {
      publication = `${paper.year}`;
    }
    
    return `${authors}. ${title} ${publication}.`.trim().replace(/\s+/g, ' ');
  }

  /**
   * Format a paper citation in Chicago style
   * 
   * @param paper - Paper to cite
   * @returns Chicago citation string
   */
  public formatChicago(paper: CitationPaper): string {
    const authors = this.formatAuthors(paper.authors, 'Chicago');
    const title = `"${paper.title}."`;
    
    let publication = '';
    if (paper.journal) {
      // Journal article
      publication = `${paper.journal}`;
      if (paper.volume) {
        publication += ` ${paper.volume}`;
        if (paper.issue) {
          publication += `, no. ${paper.issue}`;
        }
      }
      if (paper.year) {
        publication += ` (${paper.year})`;
      }
      if (paper.pages) {
        publication += `: ${paper.pages}`;
      }
    } else if (paper.conference) {
      // Conference paper
      publication = `In ${paper.conference}`;
      if (paper.year) {
        publication += `, ${paper.year}`;
      }
      if (paper.pages) {
        publication += `, ${paper.pages}`;
      }
      if (paper.publisher) {
        publication += `. ${paper.publisher}`;
      }
    } else if (paper.publisher) {
      // Book or report
      publication = `${paper.publisher}`;
      if (paper.year) {
        publication += `, ${paper.year}`;
      }
    } else if (paper.year) {
      publication = `${paper.year}`;
    }
    
    return `${authors}. ${title} ${publication}.`.trim().replace(/\s+/g, ' ');
  }

  /**
   * Format a paper citation in IEEE style
   * 
   * @param paper - Paper to cite
   * @returns IEEE citation string
   */
  public formatIEEE(paper: CitationPaper): string {
    const authors = this.formatAuthors(paper.authors, 'IEEE');
    const title = `"${paper.title},"`;
    
    let publication = '';
    if (paper.journal) {
      // Journal article
      publication = `${paper.journal}`;
      if (paper.volume) {
        publication += `, vol. ${paper.volume}`;
        if (paper.issue) {
          publication += `, no. ${paper.issue}`;
        }
      }
      if (paper.pages) {
        publication += `, pp. ${paper.pages}`;
      }
      if (paper.year) {
        publication += `, ${paper.year}`;
      }
    } else if (paper.conference) {
      // Conference paper
      publication = `in ${paper.conference}`;
      if (paper.year) {
        publication += `, ${paper.year}`;
      }
      if (paper.pages) {
        publication += `, pp. ${paper.pages}`;
      }
    } else if (paper.publisher) {
      // Book or report
      publication = `${paper.publisher}`;
      if (paper.year) {
        publication += `, ${paper.year}`;
      }
    } else if (paper.year) {
      publication = `${paper.year}`;
    }
    
    const doi = paper.doi ? `DOI: ${paper.doi}.` : '';
    
    return `${authors}, ${title} ${publication}. ${doi}`.trim().replace(/\s+/g, ' ');
  }

  /**
   * Format a paper citation in Harvard style
   * 
   * @param paper - Paper to cite
   * @returns Harvard citation string
   */
  public formatHarvard(paper: CitationPaper): string {
    const authors = this.formatAuthors(paper.authors, 'Harvard');
    const year = paper.year ? `(${paper.year})` : '';
    const title = `'${paper.title}'`;
    
    let publication = '';
    if (paper.journal) {
      // Journal article
      publication = `${paper.journal}`;
      if (paper.volume) {
        publication += `, ${paper.volume}`;
        if (paper.issue) {
          publication += `(${paper.issue})`;
        }
      }
      if (paper.pages) {
        publication += `, pp. ${paper.pages}`;
      }
    } else if (paper.conference) {
      // Conference paper
      publication = `in ${paper.conference}`;
      if (paper.pages) {
        publication += `, pp. ${paper.pages}`;
      }
      if (paper.publisher) {
        publication += `, ${paper.publisher}`;
      }
    } else if (paper.publisher) {
      // Book or report
      publication = `${paper.publisher}`;
    }
    
    return `${authors} ${year}, ${title}, ${publication}.`.trim().replace(/\s+/g, ' ');
  }

  /**
   * Format a paper citation in Vancouver style
   * 
   * @param paper - Paper to cite
   * @returns Vancouver citation string
   */
  public formatVancouver(paper: CitationPaper): string {
    const authors = this.formatAuthors(paper.authors, 'Vancouver');
    const title = `${paper.title}.`;
    
    let publication = '';
    if (paper.journal) {
      // Journal article
      publication = `${paper.journal} `;
      if (paper.year) {
        publication += `${paper.year}`;
      }
      if (paper.volume) {
        publication += `;${paper.volume}`;
        if (paper.issue) {
          publication += `(${paper.issue})`;
        }
      }
      if (paper.pages) {
        publication += `:${paper.pages}`;
      }
    } else if (paper.conference) {
      // Conference paper
      publication = `In: ${paper.conference}. `;
      if (paper.year) {
        publication += `${paper.year}`;
      }
      if (paper.pages) {
        publication += `: ${paper.pages}`;
      }
      if (paper.publisher) {
        publication += `. ${paper.publisher}`;
      }
    } else if (paper.publisher) {
      // Book or report
      publication = `${paper.publisher}`;
      if (paper.year) {
        publication += `; ${paper.year}`;
      }
    } else if (paper.year) {
      publication = `${paper.year}`;
    }
    
    return `${authors}. ${title} ${publication}.`.trim().replace(/\s+/g, ' ');
  }

  /**
   * Format a paper as a BibTeX entry
   * 
   * @param paper - Paper to format
   * @returns BibTeX entry string
   */
  public formatBibTeX(paper: CitationPaper): string {
    const bibEntry = this.toBibTeXEntry(paper);
    let output = `@${bibEntry.type}{${bibEntry.id},\n`;
    
    // Add each field
    Object.entries(bibEntry.fields).forEach(([key, value]) => {
      if (value) {
        output += `  ${key} = {${value}},\n`;
      }
    });
    
    // Remove the trailing comma and add closing brace
    output = output.slice(0, -2);
    output += '\n}';
    
    return output;
  }

  /**
   * Convert a paper to a BibTeX entry
   * 
   * @param paper - Paper to convert
   * @returns BibTeX entry object
   */
  private toBibTeXEntry(paper: CitationPaper): BibTeXEntry {
    // Generate a BibTeX ID
    const id = paper.id || this.generateBibTeXId(paper);
    
    // Determine entry type
    let type: BibTeXEntry['type'] = 'misc';
    if (paper.journal) {
      type = 'article';
    } else if (paper.conference) {
      type = 'inproceedings';
    } else if (paper.publisher && !paper.journal && !paper.conference) {
      type = 'book';
    }
    
    // Format authors
    const author = this.formatAuthors(paper.authors, 'BibTeX');
    
    // Create fields
    const fields: BibTeXEntry['fields'] = {
      title: paper.title,
      author,
    };
    
    // Add optional fields based on type
    if (paper.year) {
      fields.year = paper.year.toString();
    }
    
    if (type === 'article') {
      fields.journal = paper.journal;
      if (paper.volume) fields.volume = paper.volume.toString();
      if (paper.issue) fields.number = paper.issue.toString();
      if (paper.pages) fields.pages = paper.pages;
    } else if (type === 'inproceedings') {
      fields.booktitle = paper.conference;
      if (paper.pages) fields.pages = paper.pages;
      if (paper.publisher) fields.publisher = paper.publisher;
    } else if (type === 'book') {
      if (paper.publisher) fields.publisher = paper.publisher;
    }
    
    // Add DOI, URL, etc.
    if (paper.doi) fields.doi = paper.doi;
    if (paper.url) fields.url = paper.url;
    if (paper.arxivId) fields.note = `arXiv:${paper.arxivId}`;
    
    return {
      type,
      id,
      fields
    };
  }

  /**
   * Generate a BibTeX ID for a paper
   * 
   * @param paper - Paper to generate ID for
   * @returns BibTeX ID
   */
  private generateBibTeXId(paper: CitationPaper): string {
    // Get the first author's last name or use "unknown"
    let firstAuthorName = 'unknown';
    if (paper.authors && paper.authors.length > 0) {
      const firstAuthor = paper.authors[0];
      const parts = firstAuthor.split(' ');
      firstAuthorName = parts[parts.length - 1] || 'unknown';
    }
    
    // Generate ID in the format: lastname + year + first word of title
    const year = paper.year?.toString() || 'xxxx';
    const firstTitleWord = paper.title.split(' ')[0].toLowerCase().replace(/[^a-z0-9]/g, '');
    
    return `${firstAuthorName.toLowerCase()}${year}${firstTitleWord}`;
  }

  /**
   * Format references in the specified citation style
   * 
   * @param papers - Array of papers to include in references
   * @param style - Citation style
   * @returns Formatted references string
   */
  public formatReferences(papers: CitationPaper[], style: CitationStyle): string {
    if (style === 'BibTeX') {
      // For BibTeX, we output the entire bibliography
      return papers.map(paper => this.formatBibTeX(paper)).join('\n\n');
    }
    
    // For other styles, we create a numbered reference list
    return papers.map(paper => this.cite(paper, style)).join('\n\n');
  }

  /**
   * Export references in BibTeX format
   * 
   * @param papers - Array of papers to include in the export
   * @returns BibTeX string
   */
  public exportBibTeX(papers: CitationPaper[]): string {
    return papers.map(paper => this.formatBibTeX(paper)).join('\n\n');
  }

  /**
   * Create a citation manager from Paper objects
   * 
   * @param papers - Array of Paper objects
   * @returns New CitationManager instance with the specified papers
   */
  public static fromPapers(papers: Paper[]): CitationManager {
    const manager = new CitationManager();
    
    papers.forEach(paper => {
      const citationPaper: CitationPaper = {
        id: paper.id,
        title: paper.title,
        authors: Array.isArray(paper.authors) ? paper.authors : [paper.authors],
        year: paper.year,
        url: paper.url,
        abstract: paper.abstract,
        // Other fields might not be available in the Paper type
      };
      
      manager.addPaper(citationPaper);
    });
    
    return manager;
  }

  /**
   * Convert research API result to CitationPaper
   * 
   * @param result - Research result object
   * @returns CitationPaper object
   */
  public static fromResearchResult(result: any): CitationPaper {
    // Extract author information - handle different formats
    let authors: string[] = [];
    if (typeof result.authors === 'string') {
      // Split author string on commas
      authors = result.authors.split(/,\s*/);
    } else if (Array.isArray(result.authors)) {
      authors = result.authors;
    }
    
    return {
      id: result.id || `paper-${Date.now()}`,
      title: result.title || 'Untitled',
      authors,
      year: result.year || result.date || undefined,
      journal: result.journal || result.publication || undefined,
      conference: result.conference || undefined,
      url: result.url || result.pdfUrl || undefined,
      doi: result.doi || undefined,
      arxivId: result.arxivId || (result.url?.includes('arxiv.org') ? result.url.split('/').pop() : undefined),
      abstract: result.abstract || undefined
    };
  }
}