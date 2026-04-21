const { test, expect } = require('@playwright/test');

test('registers successfully with valid inputs', async ({ page }) => {
  const email = `valid_${Date.now()}@example.com`;

  await page.goto('/register.html');
  await page.fill('#email', email);
  await page.fill('#password', 'password123');
  await page.fill('#confirm_password', 'password123');
  await page.click('button[type="submit"]');

  await expect(page.locator('#message')).toHaveText('registration successful');
  const token = await page.evaluate(() => localStorage.getItem('jwt_token'));
  expect(token).toBeTruthy();
});

test('shows frontend validation for short register password', async ({ page }) => {
  await page.goto('/register.html');
  await page.fill('#email', 'short@example.com');
  await page.fill('#password', 'short');
  await page.fill('#confirm_password', 'short');
  await page.click('button[type="submit"]');

  await expect(page.locator('#message')).toHaveText('password must be at least 8 characters');
});

test('logs in with correct credentials and stores token', async ({ page, request }) => {
  const email = `login_${Date.now()}@example.com`;
  const setupResponse = await request.post('/register', {
    data: { email, password: 'password123' },
  });
  expect(setupResponse.ok()).toBeTruthy();

  await page.goto('/login.html');
  await page.fill('#email', email);
  await page.fill('#password', 'password123');
  await page.click('button[type="submit"]');

  await expect(page.locator('#message')).toHaveText('login successful');
  const token = await page.evaluate(() => localStorage.getItem('jwt_token'));
  expect(token).toBeTruthy();
});

test('shows invalid credentials for wrong password', async ({ page, request }) => {
  const email = `wrong_${Date.now()}@example.com`;
  const setupResponse = await request.post('/register', {
    data: { email, password: 'password123' },
  });
  expect(setupResponse.ok()).toBeTruthy();

  await page.goto('/login.html');
  await page.fill('#email', email);
  await page.fill('#password', 'wrongpass1');
  await page.click('button[type="submit"]');

  await expect(page.locator('#message')).toHaveText('invalid credentials');
});
