import mongoose from 'mongoose';

const { Schema } = mongoose;
import { IItem } from './interface';

const Vector3Schema = new Schema(
  {
    x: { type: Number, required: true },
    y: { type: Number, required: true },
    z: { type: Number, required: true },
  },
  { _id: false },
);

const TimestampSchema = new Schema(
  {
    sec: { type: Number, required: true },
    nanosec: { type: Number, required: true },
  },
  { _id: false },
);

const HeaderSchema = new Schema(
  {
    stamp: { type: TimestampSchema, required: true },
    frame_id: { type: String, required: true },
  },
  { _id: false },
);

const BarcodeMetaSchema = new Schema(
  {
    barcode_type: { type: String, required: true },
    data: { type: String, required: true },
    scan_id: { type: String, default: null },
    aisle_index: { type: Number, required: true },
  },
  { _id: false },
);

const BarcodeAbsoluteSchema = new Schema(
  {
    position: { type: Vector3Schema, required: true },
    dimension: { type: Vector3Schema, required: true },
    aligned_axis: { type: String, required: true },
  },
  { _id: false },
);

const BarcodeRelativeSchema = new Schema(
  {
    header: { type: HeaderSchema, required: true },
    position: { type: Vector3Schema, required: true },
    dimension: { type: Vector3Schema, required: true },
    side: { type: String, required: true },
  },
  { _id: false },
);

const BarcodeSchema = new Schema(
  {
    meta: { type: BarcodeMetaSchema, required: true },
    absolute: { type: BarcodeAbsoluteSchema, required: true },
    relative: { type: BarcodeRelativeSchema, required: true },
    item_uuid: { type: String, required: true },
  },
  { collection: 'barcode_collection' },
);

const ItemMetaSchema = new Schema(
  {
    item_type: { type: String, required: true },
    stack: { type: [String], required: true },
    location: { type: String, required: true },
    destination: { type: String, default: null },
    available: { type: Boolean, required: true },
    aisle_index: { type: Number, required: true },
    scan_id: { type: String, default: null },
  },
  { _id: false },
);

const ItemAbsoluteSchema = new Schema(
  {
    depth_index: { type: Number, default: null },
    stack_index: { type: Number, default: null },
    position: { type: Vector3Schema, required: true },
    waypoint: { type: String, default: null },
    aligned_axis: { type: String, required: true },
  },
  { _id: false },
);

const ItemRelativeSchema = new Schema(
  {
    dimension: { type: Vector3Schema, required: true },
    side: { type: String, required: true },
  },
  { _id: false },
);

const ItemSchema = new Schema<IItem>(
  {
    barcodes: { type: [BarcodeSchema], required: true },
    meta: { type: ItemMetaSchema, required: true },
    absolute: { type: ItemAbsoluteSchema, required: true },
    relative: { type: ItemRelativeSchema, required: true },
    uuid: { type: String, required: true },
  },
  { collection: 'inventory_items' },
);

const Vector3 = mongoose.models.Vector3 || mongoose.model('Vector3', Vector3Schema);
const Timestamp = mongoose.models.Timestamp || mongoose.model('Timestamp', TimestampSchema);
const Header = mongoose.models.Header || mongoose.model('Header', HeaderSchema);
const BarcodeMeta = mongoose.models.BarcodeMeta || mongoose.model('BarcodeMeta', BarcodeMetaSchema);
const BarcodeAbsolute = mongoose.models.BarcodeAbsolute || mongoose.model('BarcodeAbsolute', BarcodeAbsoluteSchema);
const BarcodeRelative = mongoose.models.BarcodeRelative || mongoose.model('BarcodeRelative', BarcodeRelativeSchema);
const Barcode = mongoose.models.Barcode || mongoose.model('Barcode', BarcodeSchema);
const ItemMeta = mongoose.models.ItemMeta || mongoose.model('ItemMeta', ItemMetaSchema);
const ItemAbsolute = mongoose.models.ItemAbsolute || mongoose.model('ItemAbsolute', ItemAbsoluteSchema);
const ItemRelative = mongoose.models.ItemRelative || mongoose.model('ItemRelative', ItemRelativeSchema);
const Item = mongoose.models.Item || mongoose.model('Item', ItemSchema);

export { Vector3, Timestamp, Header, BarcodeMeta, BarcodeAbsolute, BarcodeRelative, Barcode, ItemMeta, ItemAbsolute, ItemRelative, Item };
