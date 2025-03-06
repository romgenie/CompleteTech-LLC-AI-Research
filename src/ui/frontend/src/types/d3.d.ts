declare module 'd3' {
  export * from '@types/d3';
  
  // Add missing simulation types
  export interface SimulationNodeDatum {
    index?: number;
    x?: number;
    y?: number;
    vx?: number;
    vy?: number;
    fx?: number | null;
    fy?: number | null;
  }
  
  export interface SimulationLinkDatum<NodeDatum> {
    source: string | NodeDatum;
    target: string | NodeDatum;
    index?: number;
  }
  
  export interface Simulation<NodeDatum, LinkDatum> {
    nodes(): NodeDatum[];
    nodes(nodes: NodeDatum[]): this;
    
    alpha(): number;
    alpha(alpha: number): this;
    
    alphaMin(): number;
    alphaMin(min: number): this;
    
    alphaDecay(): number;
    alphaDecay(decay: number): this;
    
    alphaTarget(): number;
    alphaTarget(target: number): this;
    
    velocityDecay(): number;
    velocityDecay(decay: number): this;
    
    force(name: string): any;
    force(name: string, force: any): this;
    
    find(x: number, y: number, radius?: number): NodeDatum | undefined;
    
    on(typenames: string, listener: (this: any, ...args: any[]) => void): this;
    on(typenames: string): (this: any, ...args: any[]) => void | undefined;
    
    tick(): void;
    restart(): this;
    stop(): this;
  }
  
  // Add missing selection type
  export interface Selection<GElement extends Element, Datum, PElement extends Element = null, PDatum = null> {
    attr(name: string, value: any): this;
    attr(name: string): string;
    
    style(name: string, value: any, priority?: string): this;
    style(name: string): string;
    
    property(name: string, value: any): this;
    property(name: string): any;
    
    classed(names: string, value: boolean): this;
    classed(names: string): boolean;
    
    text(value: any): this;
    text(): string;
    
    html(value: any): this;
    html(): string;
    
    append(type: string): Selection<Element, Datum, PElement, PDatum>;
    append<ChildElement extends Element>(type: string): Selection<ChildElement, Datum, PElement, PDatum>;
    
    remove(): this;
    
    data<NewDatum>(data: NewDatum[]): Selection<GElement, NewDatum, PElement, PDatum>;
    data(): Datum[];
    
    enter(): Selection<null, Datum, PElement, PDatum>;
    exit(): Selection<GElement, Datum, PElement, PDatum>;
    
    join<JoinElement extends Element>(
      enter: (enter: Selection<null, Datum, PElement, PDatum>) => Selection<JoinElement, Datum, PElement, PDatum>
    ): Selection<JoinElement, Datum, PElement, PDatum>;
    
    on(typenames: string, listener: (this: GElement, datum: Datum, index: number, groups: GElement[] | ArrayLike<GElement>) => void): this;
    on(typenames: string): (this: GElement, datum: Datum, index: number, groups: GElement[] | ArrayLike<GElement>) => void | undefined;
    
    call(fn: (selection: this, ...args: any[]) => void, ...args: any[]): this;
    
    node(): GElement | null;
    nodes(): GElement[];
    
    each(callback: (this: GElement, datum: Datum, index: number, groups: GElement[] | ArrayLike<GElement>) => void): this;
    
    filter(filter: string | ((this: GElement, datum: Datum, index: number, groups: GElement[] | ArrayLike<GElement>) => boolean)): this;
    
    merge(other: Selection<GElement, Datum, PElement, PDatum>): this;
    
    transition(name?: string): any; // Transition<GElement, Datum, PElement, PDatum>;
    
    select(selector: string | ((this: GElement, datum: Datum, index: number, groups: GElement[] | ArrayLike<GElement>) => Element | null)): Selection<Element, Datum, PElement, PDatum>;
    select<ChildElement extends Element>(selector: string | ((this: GElement, datum: Datum, index: number, groups: GElement[] | ArrayLike<GElement>) => ChildElement | null)): Selection<ChildElement, Datum, PElement, PDatum>;
    
    selectAll(selector: string | ((this: GElement, datum: Datum, index: number, groups: GElement[] | ArrayLike<GElement>) => Element[] | ArrayLike<Element>)): Selection<Element, any, GElement, Datum>;
    selectAll<ChildElement extends Element>(selector: string | ((this: GElement, datum: Datum, index: number, groups: GElement[] | ArrayLike<GElement>) => ChildElement[] | ArrayLike<ChildElement>)): Selection<ChildElement, any, GElement, Datum>;
  }
  
  // Add missing zoom types
  export function zoomTransform(node: any): any;
  export const zoomIdentity: any;
  
  // Add missing drag types
  export function drag<Element extends SVGElement, Datum>(): any;
  
  // Selection factory functions
  export function select(selector: string | Element): Selection<Element, any, null, undefined>;
  export function select<GElement extends Element>(selector: string | GElement): Selection<GElement, any, null, undefined>;
  
  export function selectAll(selector: string | Element[] | NodeListOf<Element>): Selection<Element, any, null, undefined>;
  export function selectAll<GElement extends Element>(selector: string | GElement[] | NodeListOf<GElement>): Selection<GElement, any, null, undefined>;
}