import { Document } from 'mongoose';

interface IVector3 {
  x: number;
  y: number;
  z: number;
}

interface ITimestamp {
  sec: number;
  nanosec: number;
}

interface IHeader {
  stamp: ITimestamp;
  frame_id: string;
}

interface IBarcodeMeta {
  barcode_type: string;
  data: string;
  scan_id?: string;
  aisle_index: number;
}

interface IBarcodeAbsolute {
  position: IVector3;
  dimension: IVector3;
  aligned_axis: string;
}

interface IBarcodeRelative {
  header: IHeader;
  position: IVector3;
  dimension: IVector3;
  side: string;
}

interface IBarcode {
  meta: IBarcodeMeta;
  absolute: IBarcodeAbsolute;
  relative: IBarcodeRelative;
  item_uuid: string;
}

interface IItemMeta {
  item_type: string;
  stack: string[];
  location: string;
  destination?: string;
  available: boolean;
  aisle_index: number;
  scan_id?: string;
}

interface IItemAbsolute {
  depth_index?: number;
  stack_index?: number;
  position: IVector3;
  waypoint?: string;
  aligned_axis: string;
}

interface IItemRelative {
  dimension: IVector3;
  side: string;
}

interface IItem {
  barcodes: IBarcode[];
  meta: IItemMeta;
  absolute: IItemAbsolute;
  relative: IItemRelative;
  uuid: string;
}

export type {
  IVector3,
  ITimestamp,
  IHeader,
  IBarcodeMeta,
  IBarcodeAbsolute,
  IBarcodeRelative,
  IBarcode,
  IItemMeta,
  IItemAbsolute,
  IItemRelative,
  IItem,
};
