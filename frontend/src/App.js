import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { getChoseong } from 'es-hangul';

const API_BASE_URL = 'http://localhost:5000/api';

// 띄어쓰기 및 공백 정규화 함수
const normalizeText = (text) => {
  return text.replace(/\s+/g, '').toLowerCase();
};

// 초성인지 확인하는 함수
const isChoseongOnly = (str) => {
  const choseongPattern = /^[ㄱ-ㅎ]+$/;
  return choseongPattern.test(str);
};

// 한글 검색 함수 (초성 검색 + 일반 검색 지원)
const matchesSearch = (target, search) => {
  if (!search) return true;
  
  const normalizedTarget = normalizeText(target);
  const normalizedSearch = normalizeText(search);
  
  if (normalizedTarget.includes(normalizedSearch)) {
    return true;
  }
  
  if (isChoseongOnly(normalizedSearch)) {
    const targetChoseong = getChoseong(target).replace(/\s+/g, '');
    if (targetChoseong.includes(normalizedSearch)) {
      return true;
    }
  }
  
  return false;
};

function App() {
  const [notices, setNotices] = useState([]);
  const [sources, setSources] = useState({});
  const [sourceCounts, setSourceCounts] = useState({});
  const [allTags, setAllTags] = useState([]);
  const [selectedSource, setSelectedSource] = useState(null); // null = 전체
  const [selectedTag, setSelectedTag] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchNotices = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/all`);
      if (response.data.success) {
        setNotices(response.data.notices);
        setSources(response.data.sources);
        setSourceCounts(response.data.sourceCounts || {});
        setAllTags(response.data.tags.sort());
      } else {
        setError('데이터를 불러오는데 실패했습니다.');
      }
    } catch (err) {
      setError('서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotices();
  }, [fetchNotices]);

  // 태그 정규화 및 카운트
  const { tagCounts, frequentTags } = useMemo(() => {
    const counts = {};
    
    notices.forEach(notice => {
      notice.tags.forEach(tag => {
        const normalized = normalizeText(tag);
        counts[normalized] = counts[normalized] || { count: 0, original: tag };
        counts[normalized].count += 1;
      });
    });
    
    const frequent = Object.entries(counts)
      .filter(([_, data]) => data.count >= 2)
      .map(([normalized, data]) => ({ normalized, original: data.original, count: data.count }))
      .sort((a, b) => a.original.localeCompare(b.original));
    
    return { tagCounts: counts, frequentTags: frequent };
  }, [notices]);

  const toggleSource = (sourceKey) => {
    setSelectedSource(prev => prev === sourceKey ? null : sourceKey);
  };

  const toggleTag = (tag) => {
    const normalizedTag = normalizeText(tag);
    setSelectedTag(prev => {
      const prevNormalized = prev ? normalizeText(prev) : null;
      return prevNormalized === normalizedTag ? null : tag;
    });
  };

  const clearFilters = () => {
    setSelectedSource(null);
    setSelectedTag(null);
    setSearchText('');
  };

  const filteredNotices = useMemo(() => {
    let filtered = notices;
    
    // 소스 필터
    if (selectedSource) {
      filtered = filtered.filter(notice => notice.source === selectedSource);
    }
    
    // 태그 필터
    if (selectedTag) {
      const normalizedSelectedTag = normalizeText(selectedTag);
      filtered = filtered.filter(notice => 
        notice.tags.some(tag => normalizeText(tag) === normalizedSelectedTag)
      );
    }
    
    // 텍스트 검색
    if (searchText.trim()) {
      filtered = filtered.filter(notice => 
        matchesSearch(notice.title, searchText) ||
        notice.tags.some(tag => matchesSearch(tag, searchText))
      );
    }
    
    return filtered;
  }, [notices, selectedSource, selectedTag, searchText]);

  const totalCount = notices.length;
  const filteredCount = filteredNotices.length;

  if (error) {
    return (
      <div className="app">
        <div className="header">
          <h1>🔔 호서대학교 공지사항</h1>
          <p>통합 공지사항을 한 눈에</p>
        </div>
        <div className="error">
          <p>⚠️ {error}</p>
          <button onClick={fetchNotices}>다시 시도</button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="header">
        <h1>🔔 호서대학교 공지사항</h1>
        <p>통합 공지사항을 한 눈에</p>
        <button 
          className="refresh-btn" 
          onClick={fetchNotices}
          disabled={loading}
        >
          {loading ? '로딩 중...' : '🔄 새로고침'}
        </button>
      </div>

      {/* 소스 필터 */}
      <div className="filter-section source-filter">
        <h3>📌 사이트 필터</h3>
        <div className="source-buttons">
          <button
            className={`source-btn ${selectedSource === null ? 'active' : ''}`}
            onClick={() => setSelectedSource(null)}
          >
            전체 ({totalCount})
          </button>
          {Object.entries(sources).map(([key, source]) => (
            <button
              key={key}
              className={`source-btn ${selectedSource === key ? 'active' : ''}`}
              style={{
                '--source-color': source.color,
                borderColor: selectedSource === key ? source.color : 'transparent',
                backgroundColor: selectedSource === key ? source.color : 'white',
                color: selectedSource === key ? 'white' : '#333'
              }}
              onClick={() => toggleSource(key)}
            >
              {source.icon} {source.name} ({sourceCounts[key] || 0})
            </button>
          ))}
        </div>
      </div>

      {/* 검색 및 태그 필터 */}
      <div className="filter-section">
        <h3>🔍 검색 및 태그 필터</h3>
        
        <div className="search-box">
          <input
            type="text"
            placeholder="제목 또는 태그로 검색... (초성 검색 지원: ㄱㅈㅅ)"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            className="search-input"
          />
          {searchText && (
            <button 
              className="search-clear" 
              onClick={() => setSearchText('')}
            >
              ✕
            </button>
          )}
        </div>

        {frequentTags.length > 0 && (
          <div className="tag-filter-section">
            <p className="filter-hint">자주 등장하는 태그 (2회 이상)</p>
            <div className="filter-tags">
              {frequentTags.map(({ normalized, original, count }) => (
                <button
                  key={normalized}
                  className={`filter-tag ${selectedTag && normalizeText(selectedTag) === normalized ? 'active' : ''}`}
                  onClick={() => toggleTag(original)}
                >
                  {original} <span className="tag-count">({count})</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {(selectedSource || selectedTag || searchText) && (
          <button className="clear-filter" onClick={clearFilters}>
            ✕ 필터 초기화
          </button>
        )}
      </div>

      {/* 결과 카운트 */}
      <div className="result-count">
        검색 결과: <strong>{filteredCount}</strong>건
        {(selectedSource || selectedTag || searchText) && ` (전체 ${totalCount}건 중)`}
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>공지사항을 불러오는 중...</p>
          <p style={{ fontSize: '0.85rem', marginTop: '10px', opacity: 0.7 }}>
            (처음 로딩 시 시간이 걸릴 수 있습니다)
          </p>
        </div>
      ) : (
        <div className="unified-notice-list">
          {filteredNotices.length === 0 ? (
            <div className="notice-item empty">
              <p>필터에 맞는 공지사항이 없습니다.</p>
            </div>
          ) : (
            filteredNotices.map((notice) => (
              <NoticeItem key={notice.id} notice={notice} />
            ))
          )}
        </div>
      )}
    </div>
  );
}

function NoticeItem({ notice }) {
  return (
    <div className="notice-item">
      <div className="notice-header">
        <span 
          className="source-badge"
          style={{ backgroundColor: notice.sourceColor }}
        >
          {notice.sourceIcon} {notice.sourceName}
        </span>
        {notice.status && (
          <span 
            className={`status-badge ${notice.status === '마감' ? 'status-closed' : 'status-open'}`}
          >
            {notice.status}
          </span>
        )}
        <span className="notice-date">{notice.date}</span>
      </div>
      <div className="notice-title">
        <a href={notice.link} target="_blank" rel="noopener noreferrer">
          {notice.title}
        </a>
      </div>
      {notice.tags.length > 0 && (
        <div className="notice-tags">
          {notice.tags.map((tag, i) => (
            <span key={i} className="notice-tag">{tag}</span>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
