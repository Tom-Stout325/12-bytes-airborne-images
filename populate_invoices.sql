BEGIN;

INSERT INTO finance_invoice (invoice_numb, client_id, event, location, keyword_id, service_id, amount, date, due, paid)
VALUES
    ('INV001', (SELECT id FROM finance_client WHERE business = 'NHRA' LIMIT 1), NULL, 'Bristol', (SELECT id FROM finance_keyword WHERE name = 'Bristol' LIMIT 1), (SELECT id FROM finance_service WHERE service = 'Drone Services' LIMIT 1), 1250.00, '2023-06-28', '2023-08-12', 'Yes'),
    ('INV002', (SELECT id FROM finance_client WHERE business = 'NHRA' LIMIT 1), NULL, 'Chicago', (SELECT id FROM finance_keyword WHERE name = 'Chicago' LIMIT 1), (SELECT id FROM finance_service WHERE service = 'Drone Services' LIMIT 1), 1250.00, '2023-06-28', '2023-08-12', 'Yes'),
    ('INV003', (SELECT id FROM finance_client WHERE business = 'NHRA' LIMIT 1), NULL, 'Las Vegas I', (SELECT id FROM finance_keyword WHERE name = 'Vegas I' LIMIT 1), (SELECT id FROM finance_service WHERE service = 'Drone Services' LIMIT 1), 1250.00, '2023-08-01', '2023-09-15', 'Yes');

COMMIT;