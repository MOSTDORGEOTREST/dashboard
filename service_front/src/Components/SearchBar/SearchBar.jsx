import React, { useState, useEffect } from 'react'
import './css/SearchBar.css'
import Context from '../../context'
import { useContext } from 'react'
import { useRef } from 'react'

function SearchBar({ data }) {
	const [results, setResults] = useState([])
	// const [keyword, setKeyword] = useState('')
	const [visible, setVisible] = useState(false)

	const [stopBlur, setStopBlur] = useState(false)

	const { inputType, setInputType } = useContext(Context)

	const toggleContainer = useRef()

	function updateKeyword(text) {
		// setKeyword(text)
		setInputType(text)
	}

	//will match keyword with a potenital item in our data array
	const matchName = (name, keyword) => {
		// var keyLen = keyword.length
		// name = name.toLowerCase().substring(0, keyLen)
		// if (keyword === '') return false
		// return name === keyword.toLowerCase()
		return name.toLowerCase().includes(keyword.toLowerCase())
	}

	const updateText = (text) => {
		updateKeyword(text)
		setVisible(false)
	}
	const onSearch = (text) => {
		let _visible = true
		//hide results div if input value is empty

		//check to see if we found a match, if so, add it to results
		let _results = []
		if (text !== '') {
			_results = data.filter((item) => matchName(item.name, text))
			//if we didnt find any match, hide results div
			if (results.length < 1) _visible = false
		} else {
			_results = data
		}

		//update state changes
		setVisible(_visible)
		setResults(_results)
		updateKeyword(text)
	}

	const cancelSearch = () => {
		setVisible(false)
		setResults([])
		updateKeyword('')
	}

	useEffect(() => {
		function voidCLick(e) {
			if (!toggleContainer.current) return
			if (visible && !toggleContainer.current.contains(e.target)) {
				if (results.length < 1) {
					cancelSearch()
				} else setVisible(false)
			}
		}

		document.addEventListener('click', voidCLick)

		return () => document.removeEventListener('click', voidCLick)
	}, [])

	function onInputBlur() {
		if (!stopBlur) {
			cancelSearch()
		}
	}

	//stateless component to render preview results
	const SearchPreview = ({ name, position, index, updateText }) => {
		return (
			<div
				onClick={() => updateText(name)}
				ref={toggleContainer}
				className={`search-preview ${index === 0 ? 'start' : ''}`}
			>
				<div className="first">
					<p className="name">{name}</p>
					<p className="sub-header">{position}</p>
				</div>
				<div className="clicker"></div>
			</div>
		)
	}

	return (
		<div className="auto">
			{/* <button
					onClick={() => this.cancelSearch()}
					className={`cancel-btn ${
						this.state.keyword.length > 0 ? 'active' : 'inactive'
					}`}
				>
					x
				</button> */}
			<input
				className="search-bar"
				placeholder="Выберите из списка"
				value={inputType}
				name="search"
				onFocus={(e) => onSearch(e.target.value)}
				onBlur={(e) => {
					e.preventDefault()
					e.stopPropagation()
					onInputBlur()
				}}
				onChange={(e) => onSearch(e.target.value)}
				id="search-bar-input-1"
			/>

			{visible ? (
				<div
					className="search-results"
					onMouseEnter={() => setStopBlur(true)}
					onMouseLeave={() => setStopBlur(false)}
				>
					{results.map(({ position, name }, index) => {
						return (
							<SearchPreview
								key={index}
								updateText={updateText}
								index={index}
								position={position}
								name={name}
							/>
						)
					})}
				</div>
			) : null}
		</div>
	)
}

export default SearchBar
