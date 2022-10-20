import React, { useContext, useEffect, useState } from 'react'
import Context from '../../context'
import axios from 'axios'

import './Account.css'

import DisplayCard from '../DisplayCard/DisplayCard'

import AccountChart from './AccountChart'
import AccountCharts from './AccountCharts'
import NotLogged from '../NotLogged/NotLogged'
import Table from '../Table/Table'

export default function Account({ toSummary }) {
	const { isLogged, api, setLogged } = useContext(Context)

	// Выплаты по пользователю за месяц, заполняется из /works/pay
	const [payments, setPayments] = useState({
		reports: [],
		courses: [],
		developer: 0,
	})

	// Выплаты по пользоватлю за последние 6 месяцев из /works/pay
	const [generalPays, setGeneralPays] = useState({ prizes: [], dates: [] })

	// Данные пользователя из /staff/user/
	const [accountData, setAccountData] = useState({
		full_name: '',
		rate: 0,
		calculation_percent: 0,
		developer_percent: 0,
	})

	//
	const [accountLoaded, setAccountLoaded] = useState(false)

	// Список типов работ с /works/work-types
	const [workTypes, setWorkTypes] = useState([
		{
			id: 0,
			work_name: '',
			category: '',
			price: 0,
			dev_tips: 0,
		},
	])

	//
	const [tableLoaded, setTableLoaded] = useState(false)

	//
	const [reports, setReports] = useState({ reports: [], dates: [] })

	//
	const [paysLoaded, setPaysLoaded] = useState(false)

	//
	const [currentDate, setCurrentDate] = useState('')

	//
	const [reloadData, setReloadData] = useState(true)

	/*
		Запрос и заполнение данных пользователя и выплат за текущий месяц
	*/
	useEffect(() => {
		if (!isLogged) {
			setPayments({
				reports: [],
				courses: [],
				developer: 0,
			})
			setGeneralPays({ prizes: [], dates: [] })

			setAccountData({
				full_name: '',
				rate: 0,
				calculation_percent: 0,
				developer_percent: 0,
			})
			setAccountLoaded(false)
			setWorkTypes([
				{
					id: 0,
					work_name: '',
					category: '',
					price: 0,
					dev_tips: 0,
				},
			])
			setTableLoaded(false)
			setReports({ reports: [], dates: [] })
			setPaysLoaded(false)
			setCurrentDate('')
			setReloadData(true)
			return
		}

		if (!reloadData) return

		const paymentsRequestor = axios.create()
		paymentsRequestor.interceptors.request.use(
			(config) => {
				// Код, необходимый до отправки запроса
				config.method = 'get'
				config.withCredentials = true
				return config
			},
			(error) => {
				// Обработка ошибки из запроса
				return Promise.reject(error)
			}
		)
		paymentsRequestor.interceptors.response.use(
			function(response) {
				return response
			},
			function(error) {
				// Do something with response error
				if (error.response.status === 401) {
					setLogged(false)
				}
				return { data: null }
			}
		)

		function updatePayments() {
			if (isLogged) {
				const newDate = new Date()
				const options = { year: 'numeric', month: 'short' }
				const formatdate = new Intl.DateTimeFormat('ru-RU', options)
					.format(newDate)
					.replace(' г.', '')

				setCurrentDate(formatdate)

				paymentsRequestor
					.get(`${api}staff/user/`)
					.then((response) => {
						if (response.status === 200) {
							setAccountData(response.data)
							return response.data
						}
						return null
					})
					.then((_accountData) => {
						if (_accountData) {
							paymentsRequestor
								.get(
									`${api}works/pay/${
										_accountData.id
									}?month=${new Date().getMonth() +
										1}&year=${new Date().getFullYear()}`
								)
								.then((response) => {
									if (response.status === 200) {
										const data = response.data
										if (data) {
											// const resultData = parsePayments(data)
											const _payments = {}
											if (Object.keys(data).includes('reports')) {
												let _reports_summ = 0
												Object.keys(data.reports).forEach((report_type) => {
													_reports_summ += data.reports[report_type].payment
												})
												_payments['reports'] = _reports_summ
											} else {
												_payments['reports'] = 0
											}
											if (Object.keys(data).includes('base')) {
												_payments['base'] = data.base
											} else {
												_payments['base'] = 0
											}

											if (Object.keys(data).includes('general')) {
												_payments['general'] = data.general
											} else {
												_payments['general'] = 0
											}

											if (Object.keys(data).includes('developer'))
												_payments['developer'] = data.developer
											else _payments['developer'] = 0

											if (Object.keys(data).includes('courses')) {
												let _courses_summ = 0
												Object.keys(data.courses).forEach((report_type) => {
													_courses_summ += data.courses[report_type].payment
												})
												_payments['courses'] = _courses_summ
											} else {
												_payments['courses'] = 0
											}
											setPayments(_payments)
											setAccountLoaded(true)
										}
									}
								})
						}
					})
			}
		}

		updatePayments()

		const interval = setInterval(updatePayments, 100000)

		return () => {
			clearInterval(interval)
		}
	}, [isLogged, reloadData])

	/*
		Запрос и заполнение графиков по выплатам и отчетам
	*/
	useEffect(() => {
		if (!accountLoaded) {
			return
		}

		if (!reloadData) return

		const paymentsRequestor = axios.create()
		paymentsRequestor.interceptors.request.use(
			(config) => {
				// Код, необходимый до отправки запроса
				config.method = 'get'
				config.withCredentials = true
				return config
			},
			(error) => {
				// Обработка ошибки из запроса
				return Promise.reject(error)
			}
		)
		paymentsRequestor.interceptors.response.use(
			function(response) {
				return response
			},
			function(error) {
				// Do something with response error
				if (error.response.status === 401) {
					setLogged(false)
				}
				return { data: null }
			}
		)

		async function getGeneralPays() {
			const month = [6, 5, 4, 3, 2, 1, 0]
			const _generalPaysPrizes = []
			const _generalReports = []
			const _generalPaysDates = []

			for (const i of month) {
				const date = new Date()
				date.setMonth(date.getMonth() - i)
				await paymentsRequestor
					.get(
						`${api}works/pay/${accountData.id}?month=${date.getMonth() +
							1}&year=${date.getFullYear()}`
					)
					.then((response) => {
						if (response.status === 200) {
							const data = response.data
							if (data) {
								// const resultData = parsePayments(data)
								_generalPaysPrizes.push(data.general)

								const _generalPays_item = {}
								if (Object.keys(data).includes('reports')) {
									let _reports_summ = 0
									Object.keys(data.reports).forEach((report_type) => {
										_reports_summ += data.reports[report_type].payment
									})
									_generalPays_item['reports'] = _reports_summ
								} else {
									_generalPays_item['reports'] = 0
								}

								if (Object.keys(data).includes('developer')) {
									_generalPays_item['developer'] = data.developer
								} else {
									_generalPays_item['developer'] = 0
								}

								if (Object.keys(data).includes('courses')) {
									let _courses_summ = 0
									Object.keys(data.courses).forEach((report_type) => {
										_courses_summ += data.courses[report_type].payment
									})
									_generalPays_item['courses'] = _courses_summ
								} else {
									_generalPays_item['courses'] = 0
								}

								_generalReports.push(_generalPays_item)

								const options = { year: 'numeric', month: 'short' }
								const _date = new Intl.DateTimeFormat('ru-RU', options)
									.format(date)
									.replace(' г.', '')

								_generalPaysDates.push(_date)
							}
						}
					})
			}
			if (_generalPaysPrizes.length !== 0 || _generalPaysDates.length !== 0) {
				setGeneralPays({ prizes: _generalPaysPrizes, dates: _generalPaysDates })
				setReports({ reports: _generalReports, dates: _generalPaysDates })
			} else {
				throw new Error(422)
			}
		}

		getGeneralPays()
			.then(() => {
				setPaysLoaded(true)
			})
			.catch((error) => {})
	}, [accountLoaded, reloadData])

	/*
		Запрос и заполнение данных для таблицы
	*/
	useEffect(() => {
		if (!accountLoaded) {
			return
		}

		if (!reloadData) return

		const paymentsRequestor = axios.create()
		paymentsRequestor.interceptors.request.use(
			(config) => {
				// Код, необходимый до отправки запроса
				config.method = 'get'
				config.withCredentials = true
				return config
			},
			(error) => {
				// Обработка ошибки из запроса
				return Promise.reject(error)
			}
		)
		paymentsRequestor.interceptors.response.use(
			function(response) {
				return response
			},
			function(error) {
				// Do something with response error
				if (error.response.status === 401) {
					setLogged(false)
				}
				return { data: null }
			}
		)

		paymentsRequestor
			.get(`${api}works/work-types`)
			.then((response) => {
				const _workTypes = []
				if (response.status === 200) {
					const data = response.data
					data.forEach((item) => {
						_workTypes.push({
							name: item.work_name,
							position: item.category,
							id: item.id,
						})
					})
				}
				setWorkTypes(_workTypes)
			})
			.then(() => {
				setTableLoaded(true)
				setReloadData(false)
			})
	}, [accountLoaded, reloadData])

	/*
	 * Подписи к линиям и их цвета на грфике выплат
	 */
	const linesNames = {
		courses: { title: 'Курсы', color: 'hsl(221, 24%, 32%)' },
		developer: { title: 'Разработка', color: '#3D84A8' },
		reports: { title: 'Отчеты', color: '#46CDCF' },
	}

	return isLogged ? (
		<div className="account__wrapper">
			<div className="account__general-wrapper">
				{accountLoaded ? (
					<div className="card-item account__general">
						<div className="account__general-item">
							<h3 className="account__general-value">
								{accountData.full_name.split(' ')[0]}
							</h3>
							<div className="account__general-sub">{`${
								accountData.full_name.split(' ')[1]
							} ${accountData.full_name.split(' ')[2]}`}</div>
						</div>
						<div className="account__general-item">
							<h3 className="account__general-value">{accountData.rate}</h3>
							<div className="account__general-sub">Ставка</div>
						</div>
						<div className="account__general-item">
							<h3 className="account__general-value">{`${accountData.calculation_percent}%`}</h3>
							<div className="account__general-sub">От расчетов</div>
						</div>
						<div className="account__general-item">
							<h3 className="account__general-value">{`${accountData.developer_percent}%`}</h3>
							<div className="account__general-sub">От разработки</div>
						</div>
					</div>
				) : null}

				<div className="account__pays-wrapper">
					<DisplayCard
						title="Выплата"
						prize={accountLoaded ? payments.general : 0}
						date={currentDate}
						chartLoaded={accountLoaded}
						closeBtn={false}
					/>
					<DisplayCard
						title="Протоколы"
						prize={accountLoaded ? payments.reports : 0}
						date={currentDate}
						chartLoaded={accountLoaded}
						closeBtn={false}
					/>
					<DisplayCard
						title="Разработка"
						prize={accountLoaded ? payments.developer : 0}
						date={currentDate}
						chartLoaded={accountLoaded}
						closeBtn={false}
					/>
					<DisplayCard
						title="Курсы"
						prize={accountLoaded ? payments.courses : 0}
						date={currentDate}
						chartLoaded={accountLoaded}
						closeBtn={false}
					/>
				</div>
			</div>
			<div className="account-charts__wrapper">
				<div className="chart-card card-item">
					<h1 className="">Общие выплаты</h1>
					<div className="chart-card__chart">
						{paysLoaded ? (
							<AccountChart dataset={generalPays} />
						) : (
							<div className="blank-page-ar-2"></div>
						)}
					</div>
				</div>
				<div className="chart-card card-item">
					<h1 className="">Выплаты</h1>
					<div className="chart-card__chart">
						{paysLoaded ? (
							<AccountCharts
								dataset={reports}
								linesNames={linesNames}
								reportsKeys={['courses', 'developer', 'reports']}
							/>
						) : (
							<div className="blank-page-ar-2"></div>
						)}
					</div>
				</div>
			</div>
			{tableLoaded ? (
				<Context.Provider
					value={{
						api,
						accountData,
						setReloadData,
					}}
				>
					<Table searchData={workTypes} />
				</Context.Provider>
			) : (
				<div className="blank-page-ar-2"></div>
			)}
		</div>
	) : (
		<NotLogged />
	)
}
