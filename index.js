require('dotenv').config();
const express = require('express');
const jwt = require('jsonwebtoken');
const fs = require('fs');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.set('query parser', 'extended');

app.use(cors());
app.use(express.json());

// Data file path from environment or default
const DATA_FILE = process.env.DATA_FILE || './output.json';

/**
 * Helper to load and filter data from the JSON file
 */
const getOffersData = () => {
  try {
    if (!fs.existsSync(DATA_FILE)) return [];
    return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'))
      .filter(item => item.sku_id !== null);
  } catch (error) {
    console.error(`Error loading ${DATA_FILE}:`, error.message);
    return [];
  }
};

app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  if (Object.keys(req.query).length > 0) {
    console.log('Query Keys:', Object.keys(req.query));
    console.log('Query String:', req.url.split('?')[1]);
    console.log('Parsed Query:', JSON.stringify(req.query, null, 2));
  }
  next();
});

/**
 * Middleware to verify JWT
 */
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) return res.sendStatus(401);

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      console.error('JWT Error:', err.message);
      return res.sendStatus(403);
    }
    req.user = user;
    next();
  });
};

/**
 * Route: POST /auth/token
 * Simplified OAuth2-style auth
 */
app.post('/auth/token', (req, res) => {
  const { clientId, clientSecret } = req.body;

  if (clientId === process.env.CLIENT_ID && clientSecret === process.env.CLIENT_SECRET) {
    const user = { name: 'FMUClient' };
    const accessToken = jwt.sign(user, process.env.JWT_SECRET, { expiresIn: '1h' });
    return res.json({ access_token: accessToken, token_type: 'Bearer', expires_in: 3600 });
  }

  res.status(401).json({ message: 'Invalid credentials' });
});

/**
 * Route: GET /api/offers
 * Returns filtered offers
 */
app.get('/api/offers', authenticateToken, (req, res) => {
  let filteredOffers = getOffersData();

  // filter[field]=value
  if (req.query.filter && typeof req.query.filter === 'object') {
    const filters = req.query.filter;

    filteredOffers = filteredOffers.filter(item => {
      // Usamos Object.keys(filters).every para garantir que TODOS os filtros batam
      return Object.keys(filters).every(key => {
        const filterValue = String(filters[key]).trim(); // Valor do filtro na URL
        const itemValue = item[key]; // Valor no objeto (pode ser number, string ou null)

        // Se o valor no item for null ou undefined, só bate se o filtro for "null" ou vazio
        if (itemValue === null || itemValue === undefined) {
          return filterValue === "null" || filterValue === "";
        }

        // Comparação de string ignorando espaços extras e case
        return String(itemValue).trim() === filterValue;
      });
    });
    console.log(`[FILTER] filters: ${JSON.stringify(filters)} | total: ${filteredOffers.length}`);
  }

  res.json({
    total: filteredOffers.length,
    data: filteredOffers
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
