import { expect, test } from '@playwright/test';

import { abrirModulo, iniciarSesion } from '../auth';
import { baseUrl } from './helpers';

test('Mantenimiento: mostrar controles y rechazar un archivo que no es SQL', async ({
  page,
}) => {
  // CP-MAN-19: Muestra mantenimiento y rechaza un archivo que no es SQL.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Mantenimiento.
  await abrirModulo(page, 'mantenimiento');

  // 3. Verificar los controles disponibles.
  await expect(page.locator('#table1')).toBeVisible();
  await expect(page.locator('#btnCrearBackup')).toBeVisible();
  await expect(
    page.locator('#formRestaurarBackup input[name="backup_file"]')
  ).toHaveAttribute('accept', '.sql');

  // 4. Rechazar un archivo con extensión no permitida sin restaurar backups.
  const response = await page.context().request.post(
    `${baseUrl}/admin?ruta=mantenimiento`,
    {
      multipart: {
        restaurar: '1',
        backup_file: {
          name: 'respaldo_invalido.txt',
          mimeType: 'text/plain',
          buffer: Buffer.from('no es un respaldo SQL'),
        },
      },
    }
  );
  expect(response.ok()).toBe(true);

  const result: { icon?: string; text?: string } = await response.json();
  expect(result.icon).toBe('error');
  expect(result.text).toBe('No se pudo restaurar.');
});
