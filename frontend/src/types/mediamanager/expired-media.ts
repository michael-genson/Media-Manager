/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type LibraryType = "movie" | "show" | "unknown";

export interface ExpiredMedia {
  media: TautulliMedia;
  mediaUrl?: string;
  user?: OverseerrUser;
}
export interface TautulliMedia {
  library: TautulliLibrary;
  mediaSummary: TautulliMediaSummary;
  mediaDetail: TautulliMediaDetail;
}
export interface TautulliLibrary {
  sectionId: string;
  sectionName: string;
  sectionType: LibraryType;
  count: number;
  isActive: boolean;
}
export interface TautulliMediaSummary {
  sectionId: string;
  ratingKey: string;
  mediaType: LibraryType;
  title: string;
  addedAt: string;
  lastPlayed?: string;
}
export interface TautulliMediaDetail {
  sectionId: string;
  ratingKey: string;
  mediaType: LibraryType;
  title: string;
  guids?: string[];
}
export interface OverseerrUser {
  id: number;
  email: string;
  username?: string;
  displayName?: string;
  plexId?: number;
  plexUsername?: string;
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}
export interface ExpiredMediaIgnoredItem {
  ratingKey: string;
  name: string;
  ttl?: number;
  id: string;
}
export interface ExpiredMediaIgnoredItemIn {
  ratingKey: string;
  name?: string;
  ttl?: number;
}
