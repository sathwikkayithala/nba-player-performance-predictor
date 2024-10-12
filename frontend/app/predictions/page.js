"use client";

import { useEffect, useState } from 'react';
import {
    Container,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
    MenuItem,
    Select,
    InputLabel,
    FormControl,
    TextField,
    TableSortLabel,
} from '@mui/material';

export default function Predictions() {
    const [season, setSeason] = useState(2025);
    const [predictions, setPredictions] = useState([]);
    const [filteredPredictions, setFilteredPredictions] = useState([]);
    const [position, setPosition] = useState("");
    const [age, setAge] = useState("");
    const [playerName, setPlayerName] = useState("");
    const [order, setOrder] = useState('desc');
    const [orderBy, setOrderBy] = useState('PTS');

    const seasons = Array.from({ length: 2026 - 2015 + 1 }, (_, i) => 2014 + i);

    // getting the predictions data
    useEffect(() => {
        const fetchPredictions = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/api/predictions/${season}/`);
                if (!response.ok) throw new Error('Failed to fetch data');
                const data = await response.json();
                console.log('Fetched predictions:', data);
                setPredictions(data);
                setFilteredPredictions(data);
            } catch (error) {
                console.error('Error fetching predictions:', error);
            }
        };
        fetchPredictions();
    }, [season]);

    // sorting functions
    useEffect(() => {
        const applyFiltersAndSort = () => {
            let filtered = predictions;

            if (position) {
                filtered = filtered.filter(pred => pred.Pos === position);
            }

            if (age) {
                filtered = filtered.filter(pred => pred.Age === parseInt(age, 10));
            }

            if (playerName) {
                filtered = filtered.filter(pred => pred.Player.toLowerCase().includes(playerName.toLowerCase()));
            }

            filtered = sortPredictions(filtered, order, orderBy);
            setFilteredPredictions(filtered);
        };

        applyFiltersAndSort();
    }, [position, age, playerName, predictions, order, orderBy]);

    const sortPredictions = (data, order, orderBy) => {
        return [...data].sort((a, b) => {
            if (typeof a[orderBy] === 'string') {
                return order === 'asc' ? a[orderBy].localeCompare(b[orderBy]) : b[orderBy].localeCompare(a[orderBy]);
            }
            return order === 'asc' ? a[orderBy] - b[orderBy] : b[orderBy] - a[orderBy];
        });
    };

    const handleSort = (column) => {
        const isAsc = orderBy === column && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(column);
    };

    const uniquePositions = [...new Set(predictions.map(pred => pred.Pos))];
    const uniqueAges = [...new Set(predictions.map(pred => pred.Age))].sort((a, b) => a - b);

    return (
        <Container className="max-w-7xl mx-auto p-4">
            <Typography variant="h4" gutterBottom className="text-center">
                Expected Player Performance Projection for the {season} Season
            </Typography>

            <FormControl variant="outlined" className="mb-4" sx={{ minWidth: 200 }}>
                <InputLabel id="season-select-label">Select Season</InputLabel>
                <Select
                    labelId="season-select-label"
                    value={season}
                    onChange={(e) => setSeason(e.target.value)}
                    label="Select Season"
                >
                    {seasons.map((year) => (
                        <MenuItem key={year} value={year}>
                            {year}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>

            <FormControl variant="outlined" className="mb-4" sx={{ minWidth: 200 }}>
                <InputLabel id="position-select-label">Select Position</InputLabel>
                <Select
                    labelId="position-select-label"
                    value={position}
                    onChange={(e) => setPosition(e.target.value)}
                    label="Select Position"
                >
                    <MenuItem value="">All Positions</MenuItem>
                    {uniquePositions.map((pos) => (
                        <MenuItem key={pos} value={pos}>
                            {pos}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>

            <FormControl variant="outlined" className="mb-4" sx={{ minWidth: 200 }}>
                <InputLabel id="age-select-label">Select Age</InputLabel>
                <Select
                    labelId="age-select-label"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    label="Select Age"
                >
                    <MenuItem value="">All Ages</MenuItem>
                    {uniqueAges.map((age) => (
                        <MenuItem key={age} value={age}>
                            {age}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>

            <TextField
                label="Search Player"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                variant="outlined"
                className="mb-4"
                sx={{ minWidth: 200 }}
            />

            <TableContainer className="w-full">
                <Table className="min-w-full divide-y divide-gray-200">
                    <TableHead>
                        <TableRow>
                            {['Player', 'Season', 'Age', 'Pos', 'STL', 'BLK', 'TRB', 'AST', 'PTS'].map((column) => (
                                <TableCell key={column}>
                                    <TableSortLabel
                                        active={orderBy === column}
                                        direction={orderBy === column ? order : 'asc'}
                                        onClick={() => handleSort(column)}
                                    >
                                        {column}
                                    </TableSortLabel>
                                </TableCell>
                            ))}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {filteredPredictions.map((prediction) => (
                            <TableRow key={`${prediction.Player}-${prediction.Season}`} className="hover:bg-gray-100">
                                <TableCell>{prediction.Player}</TableCell>
                                <TableCell>{prediction.Season}</TableCell>
                                <TableCell>{prediction.Age}</TableCell>
                                <TableCell>{prediction.Pos}</TableCell>
                                <TableCell>{prediction.STL}</TableCell>
                                <TableCell>{prediction.BLK}</TableCell>
                                <TableCell>{prediction.TRB}</TableCell>
                                <TableCell>{prediction.AST}</TableCell>
                                <TableCell>{prediction.PTS}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Container>
    );
}
