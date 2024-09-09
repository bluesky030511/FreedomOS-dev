import { Render } from '@prisma/client';
import { Data, Image, PlotData } from 'plotly.js';

import { getItemPriorityBarcode } from '@/app/(util)/item';

const DARK_BLUE = 'rgba(11, 148, 153, 0.9)';
const DARK_GREEN = 'rgba(84, 193, 68, 0.9)';
const DARK_RED = 'rgba(247, 92, 64, 0.9)';
const DARK_PURPLE = 'rgba(173, 41, 255, 0.9)';
const BLUE = 'rgba(13, 180, 185, 0.5)';
const GREEN = 'rgba(135, 211, 124, 0.5)';
const RED = 'rgba(255, 99, 71, 0.5)';
const PURPLE = 'rgba(198, 107, 255, 0.5)';

interface UsePlotData {
  data?: Render;
  imageUrl?: string;
  dataSettings: Data;
}
export const usePlotData = ({ data, imageUrl, dataSettings }: UsePlotData) => {
  const getPlotData = () => {
    const plotData: Data[] = [];
    // return empty plot if no data
    if (!data) return plotData;

    data.data.forEach(d => {
      // helper functions
      const getName = () => {
        if (d.item.meta.item_type === 'box') {
          const barcodes = d.item.barcodes;

          // name will be BARCODEDATA1 <br> BARCODEDATA2 <br> ...
          return barcodes
            .map(barcode => {
              return `(${barcode.meta.data})`;
            })
            .join('<br>');
        } else return 'empty';
      };

      const getColor = () => {
        // return blue if non empty item has a barcode else return red
        if (d.item.meta.item_type == 'box') {
          if (getItemPriorityBarcode(d.item) !== null) {
            return [ BLUE, DARK_BLUE ];
          } else if (d.item.barcodes.length > 0) {
            return [ PURPLE, DARK_PURPLE ];
          } else {
            return [ RED, DARK_RED ];
          }
        } else {
          return [ GREEN, DARK_GREEN ];
        }
      };

      const [ fillColor, lineColor ] = getColor();

      // add box traces
      plotData.push({
        x: [d.x0, d.x0, d.x1, d.x1, d.x0],
        y: [d.y0, d.y1, d.y1, d.y0, d.y0],
        name: getName(),
        hoverinfo: 'text',
        labels: [d.item.meta.item_type], // box or empty
        customdata: [d.item], // pass the item data to the plot
        marker: { color: lineColor },
        fillcolor: fillColor,
        // marker: isSelected
        //   ? { color: "#000000", width: 50 }
        //   : { color: "#FFFFFF", width: 1 },
        ...dataSettings,
      } as PlotData);

      // add barcode traces for current data entry
      d.item.barcodes.forEach(barcode => {
        // the barcode absolute position is the center of the barcode + the relative position of the barcode
        const barcodePosX = d.item.absolute.position.x + barcode.relative.position.x;
        const barcodePosY = d.item.absolute.position.y + barcode.relative.position.y;

        const x0 = barcodePosX - barcode.relative.dimension.x / 2;
        const x1 = barcodePosX + barcode.relative.dimension.x / 2;
        const y0 = barcodePosY;
        const y1 = barcodePosY + barcode.relative.dimension.y;
        plotData.push({
          x: [x0, x0, x1, x1, x0],
          y: [y0, y1, y1, y0, y0],
          name: 'barcode',
          customdata: [barcode], // pass the barcode data to the plot
          labels: ['barcode'],
          hoverinfo: 'text',
          // text: (item.uid || "No UID") + ' ' + item.label,
          fillcolor: '#000',
          marker: { color: '#FFFFFF' },
          ...dataSettings,
        } as PlotData);
      });
    });

    return plotData;
  };

  const getPlotImages = () => {
    if (!data || !imageUrl) return [];

    const x = data.img_meta.x;
    const y = data.img_meta.y;
    const width = data.img_meta.width;
    const height = data.img_meta.height;

    return [
      {
        source: imageUrl,
        xref: 'x',
        yref: 'y',
        x,
        y,
        sizex: width,
        sizey: height,
        sizing: 'stretch',
        opacity: 1,
        layer: 'below',
        visible: true,
        xanchor: 'left',
        yanchor: 'top',
      },
    ] as Image[];
  };

  return { getPlotData, getPlotImages };
};
