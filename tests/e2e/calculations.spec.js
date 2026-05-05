const { test, expect } = require('@playwright/test');

async function registerAndGetToken(request, email) {
  const response = await request.post('/register', {
    data: { email, password: 'password123' },
  });
  expect(response.ok()).toBeTruthy();
  const payload = await response.json();
  return payload.access_token;
}

test('creates, reads, updates, and deletes a calculation from the dashboard', async ({ page, request }) => {
  const email = `bread_${Date.now()}@example.com`;
  const token = await registerAndGetToken(request, email);

  await page.goto('/login.html');
  await page.evaluate((savedToken) => localStorage.setItem('jwt_token', savedToken), token);
  await page.goto('/calculations.html');

  await page.fill('#add-a', '9');
  await page.fill('#add-b', '3');
  await page.selectOption('#add-type', 'Add');
  await page.click('#add-form button[type="submit"]');

  await expect(page.locator('#calc-list .calc-item')).toHaveCount(1);

  await page.click('#calc-list .calc-item button[data-id]');
  await page.click('#read-form button[type="submit"]');
  await expect(page.locator('#read-result')).toContainText('"result": 12');

  await page.fill('#edit-a', '10');
  await page.fill('#edit-b', '5');
  await page.selectOption('#edit-type', 'Multiply');
  await page.click('#edit-form button[type="submit"]');
  await expect(page.locator('#read-result')).toContainText('"result": 50');

  await page.click('#delete-submit');
  await expect(page.locator('#calc-list .list-empty')).toHaveText('no calculations found');
});

test('shows validation error for divide by zero in add form', async ({ page, request }) => {
  const email = `invalid_${Date.now()}@example.com`;
  const token = await registerAndGetToken(request, email);

  await page.goto('/login.html');
  await page.evaluate((savedToken) => localStorage.setItem('jwt_token', savedToken), token);
  await page.goto('/calculations.html');

  await page.fill('#add-a', '7');
  await page.fill('#add-b', '0');
  await page.selectOption('#add-type', 'Divide');
  await page.click('#add-form button[type="submit"]');

  await expect(page.locator('#calc-toast .toast-text').first()).toHaveText('division by zero is not allowed');
});

test('redirects protected pages to login without a valid token', async ({ page }) => {
  await page.goto('/calculations.html');
  await expect(page).toHaveURL(/\/login\.html$/);

  await page.goto('/account.html');
  await expect(page).toHaveURL(/\/login\.html$/);
});

test('redirects invalid tokens back to login', async ({ page }) => {
  await page.goto('/login.html');
  await page.evaluate(() => localStorage.setItem('jwt_token', 'bad-token-value'));
  await page.goto('/calculations.html');

  await expect(page).toHaveURL(/\/login\.html$/);
});
