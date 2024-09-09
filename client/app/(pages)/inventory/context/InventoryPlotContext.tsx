import { Barcode, Item } from '@prisma/client';
import { createContext, useState } from 'react';

export interface SelectedItemBase {
  itemType: string;
}
export interface Batchable extends SelectedItemBase {
  itemType: 'box' | 'empty';
  item: Item;
}

export interface Unbatchable extends SelectedItemBase {
  itemType: 'barcode';
  item: Barcode;
}

export type SelectedItem = Batchable | Unbatchable;

export interface BatchableCartItem {
  batchable: Batchable;
  jobType?: string;
  vendor?: string;
  destination_uuid?: string;
}

interface InventoryPlotContextType {
  selectedItem?: SelectedItem;
  setSelectedItem: (item: SelectedItem) => void;
  // Batchable for batchs [IMPORTANT]
  batchableCart: BatchableCartItem[];
  setBatchableCart: (items: BatchableCartItem[]) => void;
  updateCartItem: (newCartItem: BatchableCartItem) => void;
  deleteCartItem: (carItem: BatchableCartItem) => void;

  // Robot items
  robotBatchables: Batchable[];
  setRobotBatchables: (items: Batchable[]) => void;
}
export const InventoryPlotContext = createContext<InventoryPlotContextType>({} as InventoryPlotContextType);

export const InventoryPlotProvider = ({ children }: { children: React.ReactNode }) => {
  const [selectedItem, setSelectedItem] = useState<SelectedItem>({} as SelectedItem);
  const [robotBatchables, setRobotBatchables] = useState<Batchable[]>([]);
  const [batchableCart, setBatchableCart] = useState<BatchableCartItem[]>([]);

  const updateCartItem = (newCartItem: BatchableCartItem) => {
    const updatedCart = batchableCart.map(cartItem => {
      if (cartItem.batchable.item.uuid === newCartItem.batchable.item.uuid) {
        return newCartItem;
      }
      return cartItem;
    });
    setBatchableCart(updatedCart);
  };

  const deleteCartItem = (batchable: BatchableCartItem) => {
    const updatedCart = batchableCart.filter(cartItem => cartItem.batchable.item.uuid !== batchable.batchable.item.uuid);
    setBatchableCart(updatedCart);
  };

  return (
    <InventoryPlotContext.Provider
      value={{
        selectedItem,
        setSelectedItem,
        batchableCart,
        setBatchableCart,
        updateCartItem,
        deleteCartItem,
        robotBatchables,
        setRobotBatchables,
      }}
    >
      {children}
    </InventoryPlotContext.Provider>
  );
};
