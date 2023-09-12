/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type QBTState =
  | "allocating"
  | "checkingDL"
  | "checkingResumeData"
  | "checkingUP"
  | "downloading"
  | "error"
  | "forcedDL"
  | "forcedUP"
  | "metaDL"
  | "missingFiles"
  | "moving"
  | "pausedDL"
  | "pausedUP"
  | "queuedDL"
  | "queuedUP"
  | "stalledDL"
  | "stalledUP"
  | "unknown"
  | "uploading";
export type LibraryType = "movie" | "show" | "unknown";

export interface BaseMediaManagerMedia {
  id: string;
  dbId: string;
  title: string;
  tags?: string[];
  path: string;
  rootFolderPath: string;
}
export interface MediaManagerTag {
  id: string;
  label: string;
}
export interface OmbiUser {
  id: string;
  userName: string;
  emailAddress: string;
  alias: string;
  lastLoggedIn?: string;
  hasLoggedIn: boolean;
}
export interface QBTTorrent {
  hash: string;
  addedOn: string;
  amountLeft?: FileSize;
  lastActivity?: string;
  category?: string;
  size?: FileSize;
  totalSize?: FileSize;
  completed?: FileSize;
  completedOn?: string;
  progress?: Percent;
  downloaded?: FileSize;
  dlspeed?: FileSize;
  uploaded?: FileSize;
  upspeed?: FileSize;
  state: QBTState;
  numSeeds?: number;
  numLeechs?: number;
  polledAt?: string;
}
export interface FileSize {
  bytes: number;
}
export interface Percent {
  value: number;
}
export interface RadarrMedia {
  id: string;
  tmdbId: string;
  title: string;
  tags?: string[];
  path: string;
  rootFolderPath: string;
}
export interface SonarrMedia {
  id: string;
  tvdbId: string;
  title: string;
  tags?: string[];
  path: string;
  rootFolderPath: string;
}
/**
 * Map of rating key to detail, when available
 */
export interface TautulliFailedDeletedMedia {
  failedItems: {
    [k: string]: TautulliMediaDetail;
  };
}
export interface TautulliMediaDetail {
  sectionId: string;
  ratingKey: string;
  mediaType: LibraryType;
  title: string;
  guids?: string[];
}
export interface TautulliLibrary {
  sectionId: string;
  sectionName: string;
  sectionType: LibraryType;
  count: number;
  isActive: boolean;
}
export interface TautulliMedia {
  library: TautulliLibrary;
  mediaSummary: TautulliMediaSummary;
  mediaDetail: TautulliMediaDetail;
}
export interface TautulliMediaSummary {
  sectionId: string;
  ratingKey: string;
  mediaType: LibraryType;
  title: string;
  addedAt: string;
  lastPlayed?: string;
}
