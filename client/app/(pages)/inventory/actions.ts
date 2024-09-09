'use server';

import { Item as ItemType, PrismaClient } from '@prisma/client';
import { get } from 'http';
import { NextResponse } from 'next/server';

import { BatchableCartItem } from './context/InventoryPlotContext';
import { IItem } from '@/app/(db)/schema/interface';
import { Item } from '@/app/(db)/schema/schema';
import { initAMQP } from '@/app/(util)/amqp';
import { getItemPriorityBarcode } from '@/app/(util)/item';
import { mongo } from '@/app/(util)/mongo';

const prisma = new PrismaClient();

export const getRobotInventory = async () => {
  await mongo.connect();
  const items = await Item.find<ItemType>({
    'meta.location': 'robot',
  }).limit(10);

  if (!items) return [];

  return JSON.parse(JSON.stringify(items)) as ItemType[];
};

interface GetRender {
  side: string;
  aisle_index: number;
}
export const getRender = async ({ side, aisle_index }: GetRender) => {
  const render = await prisma.render.findFirst({
    where: {
      meta: {
        side,
        aisle_index,
      },
    },
  });

  if (!render) return;

  const renderImageUrl = `/inventory/images?container=${render.img_meta.container_name}&blob=${render.img_meta.blob_name}`;

  return { render, imageUrl: renderImageUrl };
};

export const getJobTranslationTypes = async () => {
  const jobTranslationsTypes = await prisma.jobTranslation.findMany({
    distinct: ['generic_type'],
    select: {
      generic_type: true,
    },
  });

  return jobTranslationsTypes.map(({ generic_type }) => generic_type);
};

interface SendBatch {
  batchableCart: BatchableCartItem[];
}
export const sendBatch = async ({ batchableCart }: SendBatch) => {
  await mongo.connect();

  // check that for all store inventory or store designated job types, the destination_uuid is valid
  for (const cartItem of batchableCart) {
    if (cartItem.jobType === 'STORE_INVENTORY' || cartItem.jobType === 'STORE_DESIGNATED') {
      if (!cartItem.destination_uuid) {
        return { error: 'Please fill in all destination IDs' };
      }

      const item = await Item.findOne<IItem>({
        uuid: cartItem.destination_uuid,
      });

      if (!item) {
        return { error: `Can't find any destination item with UUID(${cartItem.destination_uuid})` };
      }
    }
  }

  const formattedBatchForAMQP = batchableCart.map(cartItem => {
    // TODO we have all the "job types" in our translation. maybe build a button group for easy selection
    const getJobType = () => {
      if (cartItem.jobType === 'FETCH_DESIGNATED') return 'INT1';
      if (cartItem.jobType === 'STORE_DESIGNATED') return 'INT2';
      return cartItem.jobType;
    };

    const getVendor = () => {
      if (cartItem.jobType === 'FETCH_DESIGNATED' || cartItem.jobType === 'STORE_DESIGNATED') return 'NLS';
      return 'RUBIC';
    };

    const getDestinationUuid = () => {
      if (cartItem.jobType === 'FETCH_DESIGNATED' || cartItem.jobType === 'STORE_DESIGNATED') return undefined;
      if (!cartItem.destination_uuid) return undefined;
      return cartItem.destination_uuid;
    };
    const destinationUuid = getDestinationUuid();

    const batch = {
      uid: getItemPriorityBarcode(cartItem.batchable.item),
      job_type: getJobType(),
      vendor: getVendor(),
      ...(destinationUuid && { destination_uuid: destinationUuid }),
    };

    // eslint-disable-next-line no-console
    console.log(batch);

    return batch;
  });

  try {
    // Connect to RabbitMQ server
    const { channel } = await initAMQP();
    await channel.assertQueue('batch/request', { durable: false });
    await channel.sendToQueue('batch/request', Buffer.from(JSON.stringify(formattedBatchForAMQP)));
    return { error: null };
  } catch (error) {
    return {
      error: 'Failed to send batch',
    };
  }
};
