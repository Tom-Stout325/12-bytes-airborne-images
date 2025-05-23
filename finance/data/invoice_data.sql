--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.5 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: finance_invoice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_invoice (id, invoice_numb, event, location, amount, date, due, client_id, keyword_id, service_id, paid_date, status) FROM stdin;
95	240047	Summit NHRA Nationals	Norwalk, OH	3000.00	2024-07-02	2024-08-02	1	12	1	0004-08-15	Paid
96	240049	Sonoma Nationals	Sonoma, CA	3000.00	2024-07-30	2024-08-30	1	14	1	2024-09-05	Paid
97	240051	Lucas Oil Nationals	Brainerd, MN	3000.00	2024-08-21	2024-09-21	1	15	1	2024-09-30	Paid
98	240052	US Nationals	Indianapolis, IN	3000.00	2024-09-07	2024-10-07	1	16	1	2024-10-10	Paid
99	240053	Pep Boys Nationals	Reading, PA	3000.00	2024-09-18	2024-10-18	1	17	1	2024-10-22	Paid
1	250104	Vegas 4 Wide	Las Vegas	3250.00	2025-04-14	2025-05-14	1	5	1	\N	Unpaid
100	240054	Midwest Nationals	St. Louis, IL	3000.00	2024-10-01	2024-11-01	1	19	1	2024-11-10	Paid
101	240055	Carolina Nationals	Charlotte, NC	3000.00	2024-10-01	2024-11-01	1	7	1	2024-11-10	Paid
34	250105	Charlotte 4-Wide Nationals	Charlotte	4000.00	2025-04-28	2025-05-28	1	6	1	\N	Unpaid
102	240056	Texas FallNationals	Dallas, TX	3000.00	2024-10-15	2024-11-14	1	20	1	2024-11-20	Paid
6	240039	ThunderNationals	Bristol	3000.00	2024-06-11	2024-07-11	1	10	1	2024-07-12	Paid
4	250101	NHRA GatorNationals	Gainesville	3250.00	2025-03-15	2025-04-12	1	1	1	2025-05-01	Paid
3	250102	NHRA Arizona Nationals	Phoenix	3250.00	2025-03-26	2025-04-26	1	2	1	2025-05-01	Paid
2	250103	NHRA Winternationals	Pomona, CA	3250.00	2025-04-02	2025-05-02	1	3	1	2025-05-06	Paid
103	240057	Nevada Nationals	Las Vegas, NV	3000.00	2024-11-08	2024-12-08	1	21	1	2024-12-26	Paid
5	240058	NHRA Finals	Pomona	3000.00	2024-11-20	2024-12-20	1	4	1	2024-12-31	Paid
85	230015	Summit NHRA Nationals	Norwalk, OH	1500.00	2023-06-25	2023-07-25	1	12	1	2023-08-15	Paid
80	230016	Mile-High Nationals	Denver, CO	1500.00	2023-07-16	2023-08-16	1	35	1	2023-08-25	Paid
87	240015	Gatornationals	Gainesville, FL	1585.79	2024-03-12	2024-04-12	1	1	1	2024-04-20	Paid
88	240016	WinterNationals	Pomona, CA	1549.78	2024-03-28	2024-04-28	1	3	1	2024-05-10	Paid
79	230017	Northwest Nationals	Seattle, WA	1500.00	2023-07-23	2023-08-23	1	13	1	2023-09-01	Paid
84	230011	Gatornationals	Gainsesville, FL	1500.00	2023-03-12	2023-04-12	1	1	1	2023-04-20	Paid
83	230012	New England Nationals	Epping, NH	1500.00	2023-04-02	2023-05-02	1	2	1	2023-05-15	Paid
82	230013	Winternationals	Pomona, CA	1500.00	2023-04-02	2023-05-02	1	3	1	2023-05-15	Paid
81	230014	NHRA Four-Wide Nationals	Las Vegas, NV	1500.00	2023-04-16	2023-05-16	1	5	1	2023-05-15	Paid
89	240018	Nevada Nationals	Phoenix, AZ	1529.99	2024-04-10	2024-05-10	1	2	1	2024-05-20	Paid
90	240019	NHRA 4-Wide Nationals	Las Vegas, NV	1561.87	2024-04-17	2024-05-18	1	5	1	2024-05-22	Paid
78	230018	Sonoma Nationals	Sonoma, CA	1548.08	2023-07-30	2023-08-30	1	14	1	2023-09-05	Paid
76	230019	Lucas Oil Nationals	Brainerd, MN	1560.19	2023-08-20	2023-09-20	1	15	1	2023-09-25	Paid
77	230020	US Nationals	Indianapolis, IN	1500.00	2023-09-05	2023-10-05	1	16	1	2023-10-15	Paid
86	230021	Pep Boys Nationals	Reading, PA	1500.00	2023-09-17	2023-10-17	1	17	1	2023-10-30	Paid
74	230022	Carolina Nationals	Charlotte, NC	1624.00	2023-09-24	2023-10-24	1	7	1	2023-10-27	Paid
73	230023	Midwest Nationals	St Louis	1559.26	2023-10-01	2023-11-02	1	19	1	2023-11-10	Paid
72	230024	Texas FallNationals	Dallas, TX	1531.70	2023-10-15	2023-11-15	1	20	1	2023-11-20	Paid
71	230025	Nevada Nationals	Las Vegas, NV	1531.71	2023-10-29	2023-11-29	1	21	1	2023-12-10	Paid
70	230026	NHRA Finals	Pomona, Ca	1598.06	2023-11-12	2023-12-12	1	4	1	2023-12-20	Paid
91	240025	Charlotte 4-Wide	Charlotte, NC	3000.00	2024-04-30	2024-05-30	1	6	1	2024-06-10	Paid
92	240033	Route 66 Nationals	Chicago, IL	3000.00	2024-05-20	2024-06-20	1	8	1	2024-07-25	Paid
94	240042	Virginia Nationals	Richmond, VA	3000.00	2024-06-24	2024-07-24	1	37	1	2024-07-30	Paid
\.


--
-- Name: finance_invoice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_invoice_id_seq', 103, true);


--
-- PostgreSQL database dump complete
--

