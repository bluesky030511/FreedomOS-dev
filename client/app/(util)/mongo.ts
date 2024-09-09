import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_CONNECTION_STRING;

class Mongo {
  private connection: typeof mongoose | null;
  private promise: Promise<typeof mongoose> | null;

  constructor() {
    this.connection = null;
    this.promise = null;
  }

  public async connect(): Promise<typeof mongoose> {
    if (this.connection) {
      return this.connection;
    }

    if (!this.promise) {
      const opts = {
        useNewUrlParser: true,
        useUnifiedTopology: true,
        bufferCommands: false,
      };

      if (!MONGODB_URI) {
        throw new Error('Please define the MONGODB_URI environment variable inside .env.local');
      }

      this.promise = mongoose.connect(MONGODB_URI, opts).then(mongoose => {
        this.connection = mongoose;
        return mongoose;
      });
    }
    this.connection = await this.promise;
    return this.connection;
  }
}

export const mongo = new Mongo();
